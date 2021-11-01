#! /usr/bin/env python
#coding=utf-8

from preload_dcdn_caches import preload_dcdn_caches
from config import load_yaml_conf
import argparse
from get_frontend_file_info_list import get_frontend_file_info_list_input
from logging_set import logging_setting
from math import ceil
from time import sleep
from compare_file_list_with_old_app import compare_file_list_with_old_app_input
from get_app_common_value import get_common_value_input
from describe_dcdn_refresh_quota import describe_dcdn_refresh_quota
from kafka_producer import kafka_massage_send, kafka_producer_massage_clean
import random
import time


def preload_dcdn_request_retry(accessKeyId, accessSecret, regionID, requestObjectStr, requestTimes, requestWaitTime):
    waitTime = requestWaitTime
    result = False

    try:
        preload_dcdn_caches(accessKeyId, accessSecret, regionID, requestObjectStr, "domestic")
    except Exception as e:
        print("* 文件预热请求失败，等待 {} 秒后重试，错误项 {}".format(waitTime,e))
        sleep(waitTime)
        if requestTimes < 2:
            requestTimes = requestTimes + 1
            print("* 文件预热请求失败，等待 {} 秒后，进行第 {} 次重试...".format(waitTime,requestTimes))
            preload_dcdn_request_retry(accessKeyId, accessSecret, regionID, requestObjectStr, requestTimes, 70)
        else:
            print("* 文件预热请求重试失败，跳过该号段文件预热...")
    else:
        print("* 文件预热请求已发送，待 DCDN 预热队列完成，等待 {} 秒...".format(waitTime))
        result = True
        sleep(waitTime)


    return result



def preload_dcdn_request_with_str(accessKeyId, accessSecret, regionID,preloadMQUse,kafkaServer,kafkaTopic,requestList, logPath):
    preloadNumPerRequest = 20
    requestNum = ceil(len(requestList)/preloadNumPerRequest)
    #print(requestNum)
    preloadRandomNum=random.randint(100,999)
    resultList = []
    for n in range(0,requestNum):
        requestObjectList = []
        for m in range(n*preloadNumPerRequest,(n+1)*preloadNumPerRequest):
            if m == len(requestList):
                break
            else:
                requestObjectList.append(requestList[m])
        requestObjectStr="\n".join(requestObjectList)
        logging_setting(logPath, "info", "生成 DCDN 预热请求字符串 start {} end {} value {}" .format(n*preloadNumPerRequest,m,requestObjectStr))
        print("\n准备对号段 {} 到 {} 文件进行 DCDN 预热操作:".format(n * preloadNumPerRequest, m))
        if preloadMQUse == "kafka":
            print("预热文件队列发送到 kafka，kafka 集群：{}，kafka topic：{}，队列随机码：{}".format(kafkaServer, kafkaTopic, preloadRandomNum))
            currentTimestamp=time.time()
            timeArray=time.localtime(int(currentTimestamp))
            timeStrftime=time.strftime("%Y-%m-%d %H:%M:%S", timeArray)
            msgID=str(preloadRandomNum)+"."+str(currentTimestamp)
            print("{} 消息ID：{}".format(timeStrftime,msgID))
            kafkaSendMsg=kafka_producer_massage_clean("dcdnPreload",timeStrftime,msgID,requestObjectStr)
            result = kafka_massage_send(kafkaServer, kafkaTopic, kafkaSendMsg)
        else:
            print("定时发送预热文件队列到阿里云，队列随机码：{}".format(preloadRandomNum))
            currentTimestamp=time.time()
            timeArray=time.localtime(int(currentTimestamp))
            msgID=str(preloadRandomNum)+"."+str(currentTimestamp)
            print("{} 消息ID：{}".format(time.strftime("%Y-%m-%d %H:%M:%S", timeArray),msgID))
            requestTimes = 0
            result = preload_dcdn_request_retry(accessKeyId, accessSecret, regionID, requestObjectStr, requestTimes, 70)
            #result=True
        print("\n号段 {} 到 {} 文件 DCDN 预热结果为 {}".format(n * preloadNumPerRequest, m, result))
        resultList.append(result)
    return resultList






def preload_dcdn_caches_list(accessKeyId, accessSecret, regionID,preloadMQUse,kafkaServer,kafkaTopic,appDomainInfo,appVersionFileInfo, logPath):
    #print(appDomainInfo)

    #print(appVersionFileInfo)

    preFixList = []

    for key in appDomainInfo:
        if appDomainInfo[key]["enable"] == True and appDomainInfo[key]["preload"] == "enable":
            preloadPath = appDomainInfo[key]["flushPath"]
            for n in appDomainInfo[key]["preloadProtocol"].split(","):
                preFix = "{}://{}{}".format(n,key,preloadPath)
                if preFix[-1] != "/":
                    preFix=preFix+"/"
                preFixList.append(preFix)
        else:
            print("域名 {} DCDN 预热未开启跳过预热\n".format(key))

    if len(preFixList) != 0:

        print("预热域名前缀 {}\n".format(preFixList))
        preloadList = appVersionFileInfo["routeURL"] + appVersionFileInfo["routePathURL"] + appVersionFileInfo[
            "forcePreload"]
        print("项目计划预热文件总个数 {}\n".format(len(preloadList)))

        PreloadRemain = int(describe_dcdn_refresh_quota(accessKeyId, accessSecret, regionID)["PreloadRemain"])
        print("DCDN 当天剩余预热 URL 数量 {} \n".format(PreloadRemain))

        if len(preloadList) <= PreloadRemain:
            print("\n——————开始进行 DCDN URL 预热——————\n")
            resultDict = {}
            for n in preFixList:
                print("\n域名前缀 {} 启动预热\n".format(n))
                requestList = []
                for m in preloadList:
                    requestList.append(n + m)
                # print(requestList,len(requestList))
                result = preload_dcdn_request_with_str(accessKeyId, accessSecret, regionID, preloadMQUse,kafkaServer,kafkaTopic,requestList, logPath)
                resultDict.update({key: result})
        else:
            print("\n项目文件数超出当天 DCDN URL 预热限制数量，跳过预热")
            resultDict = "skip"
    else:
        print("预热域名前缀列表为空或异常，跳过刷新")
        resultDict = "skip"

    return resultDict







def preload_dcdn_caches_with_new_app_input(confPath,logPath,appFileInfoPath,appName,appBuildNum,lastAppBuildNum,env,preloadWay):
    conf=load_yaml_conf(confPath)
    envConf=conf[env]

    proloadResult = dict(appName=appName,
                         appBuildNum=appBuildNum,
                         env=env)


    try:
        accessKeyId=envConf["accessKeyId"]
        accessSecret=envConf["accessSecret"]
        regionID=envConf["regionID"]
        preloadMQUse=envConf["preloadMQUse"]
        kafkaServer=list(envConf["kafkaServer"].split(","))
        kafkaTopic=envConf["kafkaTopic"]
        appDomainInfo=envConf["application"][appName]


    except Exception as e:
            print("\n——————参数传入异常或未在配置列表中找到对应项目信息——————\n跳过项目 {} DCDN 预热，错误项 {}\n".format(appName,e))
    else:

        try:
            if preloadWay == "all":
                print("\n——————预热方式：{}——————\n".format("app 全量文件URL预热"))
                appVersionFileInfo = get_frontend_file_info_list_input(appFileInfoPath, appName, appBuildNum)
                appVersionFileInfo.update(dict(forcePreload=[]))

            elif preloadWay == "update":
                forcePreload = get_common_value_input(confPath,logPath,appFileInfoPath,appName,appBuildNum,env)
                #forcePreload = ['js/nim/NIM_Web_SDK_v.js', 'js/matomo.js', 'index.html']
                appVersionFileInfo = compare_file_list_with_old_app_input(appFileInfoPath, appName, appBuildNum, lastAppBuildNum)
                appVersionFileInfo.update(dict(forcePreload=forcePreload))
                print("\n——————预热方式：{}——————\n URL 预热文件列表：\n {}".format("按 app 变更文件URL预热",appVersionFileInfo))

            logging_setting(logPath, "info", "获取项目 {} 构建号 {} 预热文件列表 {}".format(appName, appBuildNum, appVersionFileInfo))
        except Exception as e:
            print("\n——————无法获取应用版本文件列表——————\n跳过项目 {} DCDN版本配置对比，错误项 {}\n".format(appName, e))
            logging_setting(logPath, "error", "获取项目 {} 构建号 {} 当前版本文件列表失败 {}".format(appName, appBuildNum, e))
        else:
            print("\n——————获取项目 {} 构建号 {} 当前版本文件列表成功，开始进行 DCDN URL 预热——————\n".format(appName, appBuildNum))
            try:
                preloadDCDNCachesResult = preload_dcdn_caches_list(accessKeyId, accessSecret, regionID,preloadMQUse,kafkaServer,kafkaTopic,appDomainInfo,appVersionFileInfo, logPath)
            except Exception as e:
                print(e)
            else:
                print("\n——————项目 {} 构建号 {} 当前版本文件 DCDN URL 预热执行完毕——————\n 预热结果 {}\n".format(appName, appBuildNum,preloadDCDNCachesResult))

    return





if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='manual to this script')

    parser.add_argument("--conf-path", type=str, default="../config/config.yaml")
    parser.add_argument("--log-path", type=str, default="../logs/application.log")
    parser.add_argument("--app-file-info-path", type=str, default="../data/frontend-file-list-example")
    parser.add_argument("--app-name", type=str, default="null")
    parser.add_argument("--app-build-num", type=str, default="null")
    parser.add_argument("--last-app-build-num", type=str, default="null")
    parser.add_argument("--env", type=str, default="qas")
    parser.add_argument("--preload-way", type=str, default="update")


    args = parser.parse_args()

    confPath = args.conf_path
    appFileInfoPath = args.app_file_info_path
    appName = args.app_name
    appBuildNum = args.app_build_num
    lastAppBuildNum = args.last_app_build_num
    env = args.env
    logPath = args.log_path
    preloadWay = args.preload_way


    # python preload_dcdn_caches_with_new_app.py --preload-way="all"  --app-name=dearxuany-front-h5 --app-build-num=build_768 --last-app-build-num=build_767
    # python preload_dcdn_caches_with_new_app.py --app-name=dearxuany-front --app-build-num="build_293"
    preload_dcdn_caches_with_new_app_input(confPath,logPath,appFileInfoPath,appName,appBuildNum,lastAppBuildNum,env,preloadWay)
