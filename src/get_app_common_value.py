#! /usr/bin/env python
#coding=utf-8

import argparse
import os
import random
from get_frontend_file_info_list import get_frontend_file_info_list_input





def get_app_path_list_comm(fileList):
    # 随机多版本命名相同文件
    appIntersection = list(set(fileList[0]).intersection(fileList[1], fileList[2], fileList[3]))
    return appIntersection




def select_app_info_randomly(appFileInfoPath,appName,appBuildNum):
    filePathList = os.listdir(appFileInfoPath)
    appNameLen = len(appName)

    appFilePathList=[]
    for n in range(0,len(filePathList)):
        if filePathList[n][:appNameLen] == appName and filePathList[n] != appName+"-"+appBuildNum:
            appFilePathList.append(filePathList[n])

    #print(appFilePathList)
    randomPath = random.sample(appFilePathList,3)
    print("随机抽取版本 {}".format(randomPath))
    return randomPath


def get_common_value_with_diff_ver(confPath,logPath,appFileInfoPath,appName,appBuildNum,env):
    randomPath = select_app_info_randomly(appFileInfoPath, appName, appBuildNum)
    randomPath.append(appName+"-"+appBuildNum)

    randomAppFileInfo = {}
    for n in range(0,len(randomPath)):
        randomBuildNum = randomPath[n][len(appName)+1:]
        appFileInfo = get_frontend_file_info_list_input(appFileInfoPath, appName, randomBuildNum)
        appFileInfoClear = appFileInfo["routeURL"]+appFileInfo["routePathURL"]
        #appFileInfoClear = appFileInfo["routeURL"]
        randomAppFileInfo.update({randomPath[n]:appFileInfoClear})

    randomAppFileInfoList = list(randomAppFileInfo.values())

    commList = get_app_path_list_comm(randomAppFileInfoList)

    return commList


def comm_list_cleaner(commListEnd):
    # 清理 md5 命名规则文件
    commListEndMd5 = []
    for n in commListEnd:
        splitList = n.split(".")
        for m in splitList:
            if len(m)==8 or n in ['js','js/nim','static']:
                commListEndMd5.append(n)
    commListEnd = list(set(commListEnd) - set(commListEndMd5))
    return commListEnd







def get_common_value_input(confPath,logPath,appFileInfoPath,appName,appBuildNum,env):

    # 随机抽取 3 个版本+当前更新版本，对比文件列表交集，循环4次，即取“随机 12 个版本+当前版本”获取文件交集
    # 获取 12 个版本文件交集后，去除符合 md5 规则命名文件，剩余多次版本同名且不符合 md5 规则命名文件
    # 由于某些 app 测试版本命名规则和生产不一致，为防止这些版本影响校验结果，将对最终获取的结果与循环 4 次结果做比值作为可信度
    # 可信度大于 75% 结束随机，否则重新调用函数继续新一轮随机

    commListMulti = []
    commListCleanerMulti = []
    multi = 4

    print("\n——————随机抽取 app 版本获取同名文件列表——————\n")
    for n in range(0,multi):
        commListOne=get_common_value_with_diff_ver(confPath, logPath, appFileInfoPath, appName, appBuildNum, env)
        commListOneClean=comm_list_cleaner(commListOne)
        print("md5 命名文件清理后相同文件 {}\n".format(commListOneClean))
        commListMulti.append(commListOne)
        commListCleanerMulti.append(commListOneClean)

    #print(commListMulti)
    commListEnd = get_app_path_list_comm(commListMulti)
    print("\n——————随机抽取 app 版本同名文件校验结果——————\n")
    #print("随机 12 个版本对比获取 app 相同文件列表：\n{}\n".format(commListEnd))
    commListEndClean = comm_list_cleaner(commListEnd)
    print("随机结果去除 md5 命名文件（推荐刷新）：\n{}\n".format(commListEndClean))

    commListEndCleanCount = commListCleanerMulti.count(commListEndClean)
    credibility = commListEndCleanCount/len(commListCleanerMulti)*100


    if credibility > 75:
        print("结果可信度为 {}% 符合要求，结束随机抽取".format(credibility))
        return commListEndClean
    else:
        print("结果可信度为 {}% 未达标准，继续下轮随机...".format(credibility))
        return get_common_value_input(confPath,logPath,appFileInfoPath,appName,appBuildNum,env)







if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='manual to this script')

    parser.add_argument("--conf-path", type=str, default="../config/config.yaml")
    parser.add_argument("--log-path", type=str, default="../logs/application.log")
    parser.add_argument("--app-file-info-path", type=str, default="../data/frontend-file-list-example")
    parser.add_argument("--app-name", type=str, default="null")
    parser.add_argument("--app-build-num", type=str, default="null")
    parser.add_argument("--env", type=str, default="qas")


    args = parser.parse_args()

    confPath=args.conf_path
    appFileInfoPath=args.app_file_info_path
    appName=args.app_name
    appBuildNum=args.app_build_num
    env=args.env
    logPath=args.log_path


    # python get_app_common_value.py --app-name=dearxuany-front-h5 --app-build-num="build_768"
    # python get_app_common_value.py --app-name=dearxuany-front --app-build-num="build_299"
    get_common_value_input(confPath,logPath,appFileInfoPath,appName,appBuildNum,env)