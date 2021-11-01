#! /usr/bin/env python
#coding=utf-8

from config import load_yaml_conf
import argparse
from get_frontend_file_info_list import get_frontend_file_info_list_input
from get_dcdn_domain_config import get_dcdn_domain_config
from logging_set import logging_setting


def get_app_dcdn_config(accessKeyId, accessSecret, regionID, appDomainInfo):
    appDcdnConfig = {}
    for key in appDomainInfo:
        appDcdnConfig[key] = get_dcdn_domain_config(accessKeyId, accessSecret, regionID, key, "dynamic")
    return appDcdnConfig

def app_dcdn_config_cleaner(appDcdnConfig):
    appDcdnClearConfig={}
    for key in appDcdnConfig:
        appFunctionArg=appDcdnConfig[key]["DomainConfigs"]["DomainConfig"][0]["FunctionArgs"]["FunctionArg"]
        dcdnConfigID=appDcdnConfig[key]["DomainConfigs"]["DomainConfig"][0]["ConfigId"]
        for n in range(0,len(appFunctionArg)):
            if appFunctionArg[n]["ArgName"] == "static_route_path":
                staticRoutePath = appFunctionArg[n]["ArgValue"].split(" ")
            elif appFunctionArg[n]["ArgName"] == "static_route_url":
                staticRouteUrl = appFunctionArg[n]["ArgValue"].split(" ")
            elif "static_route_url" not in appFunctionArg[n]["ArgName"]:
                # 兼容使用静态类型区分动静态加速、无 static_route_url 配置的情况
                staticRouteUrl = []
                
        appDcdnClearConfig[key]=dict(staticRoutePath=staticRoutePath,staticRouteUrl=staticRouteUrl,dcdnConfigID=dcdnConfigID)
    return appDcdnClearConfig


def app_file_list_cleaner(appVersionFileInfo,appDomainInfo):
    # transform format from app version file list to domain url
    appFileListClearConfig={}

    for key in appDomainInfo:
        domainPath=appDomainInfo[key]["flushPath"]
        if domainPath[-1] != "/":
            domainPath=domainPath+"/"

        staticRoutePath=[]
        for n in range(0,len(appVersionFileInfo["routePath"])):
           staticRoutePath.append(domainPath+appVersionFileInfo["routePath"][n]+"/*")

        staticRouteUrl = []
        for n in range(0,len(appVersionFileInfo["routeURL"])):
           staticRouteUrl.append(domainPath+appVersionFileInfo["routeURL"][n])

        appFileListClearConfig.update({key:dict(staticRoutePath=staticRoutePath,staticRouteUrl=staticRouteUrl,domainPath=domainPath)})

    return appFileListClearConfig

def app_path_diff(appDcdnClearConfig,appFileListClearConfig):

    newAppDcdnConfigDiff = {}
    for key in appFileListClearConfig:
        domainName = key
        domainPath = appFileListClearConfig[key]["domainPath"]
        domainPathLen = len(domainPath)

        domainAppStaticRoutePath=appFileListClearConfig[key]["staticRoutePath"]
        domainAppStaticRouteUrl=appFileListClearConfig[key]["staticRouteUrl"]

        domainDcdnStaticRoutePath = appDcdnClearConfig[key]["staticRoutePath"]
        domainDcdnStaticRouteUrl = appDcdnClearConfig[key]["staticRouteUrl"]

        domainDcdnStaticRoutePathOfApp = []
        for n in range(0,len(domainDcdnStaticRoutePath)):
            if domainDcdnStaticRoutePath[n][:domainPathLen] == domainPath:
                domainDcdnStaticRoutePathOfApp.append(domainDcdnStaticRoutePath[n])

        domainDcdnStaticRouteUrlOfApp = []
        for n in range(0,len(domainDcdnStaticRouteUrl)):
            if domainDcdnStaticRouteUrl[n][:domainPathLen] == domainPath:
                domainDcdnStaticRouteUrlOfApp.append(domainDcdnStaticRouteUrl[n])

        # dcdn 上存在，但新版 app 已删除的路径，为应用新版本已去除的文件目录，不再需要缓存。
        # 由于 uat 和 prd 使用同一域名，uat 环境需暂时保留，prd 环境上线时删除，其余环境上线直接删除。
        routePathDelete = list(set(domainDcdnStaticRoutePathOfApp)-set(domainAppStaticRoutePath))
        routeUrlDelete = list(set(domainDcdnStaticRouteUrlOfApp)-set(domainAppStaticRouteUrl))

        # dcdn 上不存在，但新版本 app 存在路径，为应用新版本新增的文件目录，需要在 dcdn 新增缓存并配置为静态加速规则。
        # 应用更版新增文件，uat 上线的时候就需要添加到 dcdn 缓存并配置为静态加速，最好能配置预热。
        routePathAdd = list(set(domainAppStaticRoutePath)-set(domainDcdnStaticRoutePathOfApp))
        routeUrlAdd = list(set(domainAppStaticRouteUrl)-set(domainDcdnStaticRouteUrlOfApp))
        #print(routePathAdd,routeUrlAdd)

        # dcdn 上存在，新版本 app 也存在的路径，为应用新版本未修改过的文件目录，需保留 dcdn 原配置，最好刷新并预热。
        routePathCurrent = list(set(domainDcdnStaticRoutePathOfApp)&set(domainAppStaticRoutePath))
        routeUrlCurrent = list(set(domainAppStaticRouteUrl)&set(domainDcdnStaticRouteUrlOfApp))

        staticRoutePath=dict(delete=routePathDelete,add=routePathAdd,current=routePathCurrent)
        staticRouteUrl=dict(delete=routeUrlDelete,add=routeUrlAdd,current=routeUrlCurrent)

        newAppDcdnConfigDiff.update({key:dict(staticRoutePath=staticRoutePath,staticRouteUrl=staticRouteUrl)})

    return newAppDcdnConfigDiff


def compare_dcdn_config_with_new_app_input(confPath,logPath,appFileInfoPath,appName,appBuildNum,env):
    conf=load_yaml_conf(confPath)
    envConf=conf[env]

    compareResult = dict(appName=appName,
                         appBuildNum=appBuildNum,
                         env=env)


    try:
        accessKeyId=envConf["accessKeyId"]
        accessSecret=envConf["accessSecret"]
        regionID=envConf["regionID"]
        appDomainInfo=envConf["application"][appName]
    except Exception as e:
            print("\n——————参数传入异常或未在配置列表中找到对应项目信息——————\n跳过项目 {} DCDN版本配置对比，错误项 {}\n".format(appName,e))
    else:

        try:
            appVersionFileInfo = get_frontend_file_info_list_input(appFileInfoPath, appName, appBuildNum)
            logging_setting(logPath, "info", "获取项目 {} 构建号 {} 文件列表 {}".format(appName, appBuildNum, appVersionFileInfo))
        except Exception as e:
            print("\n——————无法获取应用版本文件列表——————\n跳过项目 {} DCDN版本配置对比，错误项 {}\n".format(appName, e))
            logging_setting(logPath, "error", "获取项目 {} 构建号 {} 当前版本文件列表失败 {}".format(appName, appBuildNum, e))


        try:
            appDcdnConfig=get_app_dcdn_config(accessKeyId, accessSecret, regionID, appDomainInfo)
        except Exception as e:
            logging_setting(logPath, "info", "获取项目 {} 域名当前 dcdn 配置失败 {}".format(appName, e))
        else:
            compareResult.update(dict(appDcdnConfig=appDcdnConfig))
            logging_setting(logPath, "info", "获取项目 {} 域名当前 dcdn 配置 {}".format(appName, appDcdnConfig))

            appDcdnClearConfig=app_dcdn_config_cleaner(appDcdnConfig)
            compareResult.update(dict(appDcdnClearConfig=appDcdnClearConfig))
            logging_setting(logPath, "info", "清洗项目 {} 域名当前 dcdn 配置获取静态目录及静态URL {}".format(appName,appDcdnClearConfig))
            #print(appDcdnConfig, appDcdnClearConfig)

            print("\n——————获取应用归属域名当前 DCDN 配置成功——————\n")
            for key in appDcdnClearConfig:
                print("域名 {}    DCDN ConfigID: {}".format(key,appDcdnClearConfig[key]["dcdnConfigID"]))

            appFileListClearConfig=app_file_list_cleaner(appVersionFileInfo, appDomainInfo)
            compareResult.update(dict(appFileListClearConfig=appFileListClearConfig))
            logging_setting(logPath, "info", "转换项目 {} 构建号 {} 文件列表为归属域名路径URL形式 {}".format(appName, appBuildNum,appFileListClearConfig))

            print("\n——————校验新版本应用文件路径与归属域名当前 DCDN 配置差异——————\n")
            newAppDcdnConfigDiff=app_path_diff(appDcdnClearConfig, appFileListClearConfig)
            compareResult.update(dict(newAppDcdnConfigDiff=newAppDcdnConfigDiff))
            logging_setting(logPath, "info","对比项目 {} 构建号 {} 文件列表与当前 DCDN 配置差异 {}".format(appName, appBuildNum, newAppDcdnConfigDiff))

            for key in newAppDcdnConfigDiff:
                domainDiff = newAppDcdnConfigDiff[key]
                print("域名 {} 应用名 {} 构建号 {} ：\n".format(key, appName, appBuildNum))
                for key in domainDiff:
                    if key == "staticRoutePath":
                        fileType = "目录"
                    elif key == "staticRouteUrl":
                        fileType = "文件"
                    print("* 删除{} {}  共 {} 个\n".format(fileType,domainDiff[key]["delete"],len(domainDiff[key]["delete"])))
                    print("* 新增{} {}  共 {} 个\n".format(fileType, domainDiff[key]["add"],len(domainDiff[key]["add"])))
                    print("* 未变更{}  共 {} 个\n".format(fileType, len(domainDiff[key]["current"])))


    return compareResult

    
    

     


     
     

if __name__=="__main__":
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


    # python compare_dcdn_config_with_new_app.py --app-name=dearxuany-front-h5 --app-build-num="build_716"
    compare_dcdn_config_with_new_app_input(confPath,logPath,appFileInfoPath,appName,appBuildNum,env)
