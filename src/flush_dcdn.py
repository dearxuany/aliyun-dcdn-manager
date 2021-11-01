#!/usr/bin/env python
#coding=utf-8


from aliyunsdkcore.client import AcsClient
from aliyunsdkcore.acs_exception.exceptions import ClientException
from aliyunsdkcore.acs_exception.exceptions import ServerException
from aliyunsdkdcdn.request.v20180115.RefreshDcdnObjectCachesRequest import RefreshDcdnObjectCachesRequest
from config import load_yaml_conf
from time import sleep
import datetime
import argparse


def flush_dcdn_request(accessKeyId,accessSecret,regionID,objectPath,objectType):

    client = AcsClient(accessKeyId,accessSecret,regionID)


    request = RefreshDcdnObjectCachesRequest()
    request.set_accept_format('json')


    request.set_ObjectPath(objectPath)
    request.set_ObjectType(objectType)


    response = client.do_action_with_exception(request)
    print(str(response, encoding='utf-8'))
    return 


def flush_dcdn_domain_list(accessKeyId,accessSecret,regionID,appFlushDomainInfo):
    for key in appFlushDomainInfo:
        domainName=key
        domainPath=appFlushDomainInfo[key]["flushPath"]
        protocolList=appFlushDomainInfo[key]["protocol"].split(",")
        objectType=appFlushDomainInfo[key]["flushType"]

        objectPathList=[]
        for n in range(0,len(protocolList)):
            if objectType == "Directory":
                objectPathList.append(protocolList[n]+"://"+domainName+domainPath)
            elif objectType == "File":
                filePath=appFlushDomainInfo[key]["flushURI"].split(",")
                for m in range(len(filePath)):
                    if domainPath[-1] != "/":
                        domainPath = domainPath+"/"
                    objectPathList.append(protocolList[n] + "://" + domainName + domainPath + filePath[m])

        if appFlushDomainInfo[key]["enable"] == True:
            print("\n——————即将执行 DCDN 全站加速域名刷新——————\n域名刷新列表：{}\n刷新类型：{}\n".format(objectPathList,objectType))
            for n in range(0,len(objectPathList)):
                objectPath=objectPathList[n]
                print("\n——————开始执行 DCDN 全站加速域名刷新——————\n刷新域名路径：{}\n".format(objectPath))
                # 调试代码 print(accessKeyId,accessSecret,regionID)
                if objectType == "Directory" and objectPath[-1] != "/":
                    objectPath=objectPath+"/"
                    print("Warning - 目录形式刷新域名路径 / 缺失，自动补全，补全域名路径 {}\n".format(objectPath))
                flush_dcdn_request(accessKeyId,accessSecret,regionID,objectPath,objectType)
                print("\n—————— DCDN 全站加速域名刷新执行完成——————\n已完成刷新域名路径：{}\n".format(objectPath)) 
        else:
            print("\n——————该域名未开启 DCDN 全站加速刷新——————\n域名：{}".format(key))
    return



def flush_dcdn_input():
 
    parser = argparse.ArgumentParser(description='manual to this script')

    parser.add_argument("--conf-path", type=str, default="../config/config.yaml")
    parser.add_argument("--app-name", type=str, default="full-station")
    parser.add_argument("--env", type=str, default="qas")
    
    args = parser.parse_args()

    confPath=args.conf_path
    appName=args.app_name
    env=args.env


    flushConf=load_yaml_conf(confPath)
    envflushConf=flushConf[env]

    try:
        accessKeyId=envflushConf["accessKeyId"]
        accessSecret=envflushConf["accessSecret"]
        regionID=envflushConf["regionID"]
        waitTimeBeforeFlush=envflushConf["waitTimeBeforeFlush"]
        appFlushDomainInfo=envflushConf["application"][appName]


    except Exception as e:
        print("\n——————跳过 DCDN 刷新——————\n跳过项目 {} 刷新\n参数传入异常或未在配置列表中找到对应项目信息\n错误信息： {}\n".format(appName,e))
    else:
        print("\n——————DCDN 刷新前置处理——————\n")
        print("{} 进入 DCDN 刷新前置等待时间，等待 {} 秒".format(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),waitTimeBeforeFlush))
        # 主要是等待 k8s 前端新版容器切换完毕
        sleep(waitTimeBeforeFlush)
        print("{} DCDN 刷新前置等待时间结束".format(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')))

        print("\n——————DCDN 全站加速刷新参数——————\n启用配置路径：{}\n环境：{}\n应用名：{}\n应用域名刷新项：{}\n".format(confPath,env,appName,appFlushDomainInfo))
        flush_dcdn_domain_list(accessKeyId,accessSecret,regionID,appFlushDomainInfo)


    return


if __name__=="__main__":
    # python flush_dcdn.py --app-name=dearxuany-front-h5 --env=qas
    flush_dcdn_input()


