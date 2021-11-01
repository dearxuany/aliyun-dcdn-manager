#! /usr/bin/env python
#coding=utf-8

import argparse
import os
import random

def select_app_info_randomly(appFileInfoPath,appName,appBuildNum):
    filePathList = os.listdir(appFileInfoPath)
    appNameLen = len(appName)

    appFilePathList=[]
    for n in range(0,len(filePathList)):
        if filePathList[n][:appNameLen] == appName and filePathList[n] != appName+"-"+appBuildNum:
            appFilePathList.append(filePathList[n])

    print(appFilePathList)
    randomPath = random.sample(appFilePathList,3)
    print(randomPath)
    return randomPath


def get_comm_value_input(confPath,logPath,appFileInfoPath,appName,appBuildNum,env):
    randomPath = select_app_info_randomly(appFileInfoPath, appName, appBuildNum)




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


    # python get_comm_value-test.py --app-name=dearxuany-front-h5 --app-build-num="build_715"
    get_comm_value_input(confPath,logPath,appFileInfoPath,appName,appBuildNum,env)