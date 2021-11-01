#! /usr/bin/env python
#coding=utf-8

import read_file


def frontend_filelist_cleaner(fileLineList):
    frontendFileInfo = {"routePath":[],"routeURL":[],"routePathURL":[]}
    for n in range(0,len(fileLineList)):
        if fileLineList[n][0]=="d" and fileLineList[n][-1] != "." and fileLineList[n][:4] != "dist":
            # 筛选静态目录
            frontendFileInfo["routePath"].append(fileLineList[n].split(" ")[-1])
        elif fileLineList[n][0]=="-":
            frontendFileInfo["routeURL"].append(fileLineList[n].split(" ")[-1])

    for n in range(0, len(fileLineList)):
        # dist 目录内识别 .
        # if fileLineList[n][0]=="." and fileLineList[n] != ".":
        # dist 上层目录识别 dist
        if fileLineList[n][:4]=="dist" and fileLineList[n] != "dist":
            if fileLineList[n].split("/")[1] in frontendFileInfo["routePath"]:
                frontendFileInfo["routePathURL"].append(fileLineList[n][5:])

    return frontendFileInfo




def get_frontend_file_info_list_input(appFileInfoPath,appName,appBuildNum):
    if appFileInfoPath[-1] != "/":
        appFileInfoPath=appFileInfoPath+"/"
    appFrontendInfoFile=appFileInfoPath+appName+"-"+appBuildNum

    # print("\n——————项目版本文件目录列表加载路径及内容——————\n\n{}\n".format(appFrontendInfoFile))

    #fileTotal=read_file.read_file_by_total(appFrontendInfoFile)
    #print(fileTotal)

    fileLineList=read_file.read_file_lines(appFrontendInfoFile)

    appFrontendFileList=frontend_filelist_cleaner(fileLineList)

    # print(appFrontendFileList)
    return appFrontendFileList    
     

if __name__=="__main__":
    appFileInfoPath="../data/frontend-file-list-example"
    appName="dearxuany-front-h5"
    appBuildNum="build_715"

    print(get_frontend_file_info_list_input(appFileInfoPath,appName,appBuildNum))
