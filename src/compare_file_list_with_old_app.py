#! /usr/bin/env python
#coding=utf-8

import argparse
from get_frontend_file_info_list import get_frontend_file_info_list_input


def get_diff_value_from_new_and_old_version(currentAppFileList,lastAppFileList):
    # 上个版本 app 不存在，但新版本 app 存在的文件，为应用新版本新增的文件
    routePathAdd = list(set(currentAppFileList["routePathURL"]) - set(lastAppFileList["routePathURL"]))
    routeUrlAdd = list(set(currentAppFileList["routeURL"]) - set(lastAppFileList["routeURL"]))

    return dict(routePathURL=routePathAdd,routeURL=routeUrlAdd)



def compare_file_list_with_old_app_input(appFileInfoPath,appName,appBuildNum,lastAppBuildNum):
    currentAppFileList = get_frontend_file_info_list_input(appFileInfoPath,appName,appBuildNum)
    lastAppFileList = get_frontend_file_info_list_input(appFileInfoPath,appName,lastAppBuildNum)
    #print(currentAppFileList,lastAppFileList)

    diffValue = get_diff_value_from_new_and_old_version(currentAppFileList, lastAppFileList)

    return diffValue






if __name__=="__main__":
    parser = argparse.ArgumentParser(description='manual to this script')

    parser.add_argument("--app-file-info-path", type=str, default="../data/frontend-file-list-example")
    parser.add_argument("--app-name", type=str, default="null")
    parser.add_argument("--app-build-num", type=str, default="null")
    parser.add_argument("--last-app-build-num", type=str, default="null")


    args = parser.parse_args()

    appFileInfoPath=args.app_file_info_path
    appName=args.app_name
    appBuildNum=args.app_build_num
    lastAppBuildNum=args.last_app_build_num


    # python compare_file_list_with_old_app.py --app-name=dearxuany-front-h5 --app-build-num=build_768 --last-app-build-num=build_767
    compare_file_list_with_old_app_input(logPath,appFileInfoPath,appName,appBuildNum,lastAppBuildNum)