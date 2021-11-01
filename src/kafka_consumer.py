#coding=utf-8

from kafka import KafkaConsumer
from logging_set import logging_setting
import argparse
from config import load_yaml_conf
from describe_dcdn_refresh_quota import describe_dcdn_refresh_quota
from preload_dcdn_caches_with_new_app import preload_dcdn_request_retry
from describe_dcdn_refresh_tasks import dcdn_tasks_not_completed
from time import sleep


def check_dcdn_preload_status(accessKeyId, accessSecret, regionID, requestWaitTime):
    try:
        PreloadRemain = int(describe_dcdn_refresh_quota(accessKeyId, accessSecret, regionID)["PreloadRemain"])
        tasksNotCompleted = dcdn_tasks_not_completed(accessKeyId, accessSecret, regionID)
    except Exception as e:
        logging_setting(logPath, "error", "Aliyun DCDN API return error:\n {}".format(e))
        sleep(requestWaitTime*3)
        check_dcdn_preload_status(accessKeyId, accessSecret, regionID, requestWaitTime)
    else:
        dcdnCurrentStatus={"PreloadRemain":PreloadRemain,"tasksNotCompleted":tasksNotCompleted}

    return dcdnCurrentStatus



def kafka_dcdn_preload_process(accessKeyId, accessSecret, regionID, msgValue, logPath):

    preloadList=list(msgValue["requestObjectStr"].split("\n"))
    preloadListCount=len(preloadList)

    requestWaitTime = 10

    try:
        dcdnCurrentStatus=check_dcdn_preload_status(accessKeyId, accessSecret, regionID,requestWaitTime)
        PreloadRemain=dcdnCurrentStatus["PreloadRemain"]
        tasksNotCompleted=dcdnCurrentStatus["tasksNotCompleted"]

    except Exception as e:
        logging_setting(logPath, "error", "Failing to get Aliyun DCDN preload status. {}".format(e))

    else:
        if preloadListCount <= PreloadRemain and len(tasksNotCompleted) == 0:
            logging_setting(logPath, "info",
                            "DCDN preloadRemain: {} preloadListCount: {} kafkaMsg: {}".format(PreloadRemain, preloadListCount,
                                                                                       msgValue))
            requestTimes = 0
            result = preload_dcdn_request_retry(accessKeyId, accessSecret, regionID, msgValue["requestObjectStr"], requestTimes, requestWaitTime)
            #print(result,msgValue)
            print(msgValue["msgID"])
            #sleep(10)

        elif preloadListCount > PreloadRemain:
            logging_setting(logPath, "error", "DCDN preloadRemain: {} preloadListCount: {} error kafkaMsg: {}".format(PreloadRemain,preloadListCount,msgValue))
        else:
            logging_setting(logPath, "warning",
                            "DCDN is having uncompleted tasks: {}. Waiting {} to retry. kafkaMsg: {}".format(tasksNotCompleted,requestWaitTime,msgValue))
            sleep(requestWaitTime)
            kafka_dcdn_preload_process(accessKeyId, accessSecret, regionID, msgValue, logPath)

    return



def kafka_receive_massage_process(accessKeyId, accessSecret, regionID, msgValue, logPath):
    msgValue=eval(msgValue)

    if msgValue["msgType"]=="dcdnPreload":
        kafka_dcdn_preload_process(accessKeyId, accessSecret, regionID, msgValue, logPath)
        # print(msgValue["msgID"]) # test code

    return


def kafka_massage_consumer(accessKeyId, accessSecret, regionID, kafkaServer, kafkaTopic,kafkaGroupID, logPath):
    consumer = KafkaConsumer(kafkaTopic,
                             group_id=kafkaGroupID,
                             bootstrap_servers=kafkaServer,
                             enable_auto_commit = True, # 每过一段时间自动提交所有已消费的消息（在迭代时提交）
                             auto_commit_interval_ms = 500, # 自动提交的周期（毫秒）
                             max_poll_records = 2)  # 单次消费者拉取的最大数据条数


    for msg in consumer:
        msgValue=msg.value.decode()
        logging_setting(logPath, "info", msg)
        kafka_receive_massage_process(accessKeyId, accessSecret, regionID, msgValue, logPath)

    return


def kafka_massage_consummer_input(confPath,logPath,env):
    conf=load_yaml_conf(confPath)
    envConf=conf[env]

    try:
        accessKeyId=envConf["accessKeyId"]
        accessSecret=envConf["accessSecret"]
        regionID=envConf["regionID"]
        kafkaServer=list(envConf["kafkaServer"].split(","))
        kafkaTopic=envConf["kafkaTopic"]
        kafkaGroupID=envConf["kafkaGroupID"]

    except Exception as e:
        logging_setting(logPath, "error", e)
    else:
        kafka_massage_consumer(accessKeyId, accessSecret, regionID, kafkaServer, kafkaTopic, kafkaGroupID, logPath)



if __name__=="__main__":

    #kafkaServer=['10.0.0.50:9092']
    #kafkaTopic='dev_aliyun-dcdn-preload'
    #kafkaGroupID='liyunxuan-test'
    #logPath="../logs/kafka_consumer.log"

    parser = argparse.ArgumentParser(description='manual to this script')

    parser.add_argument("--conf-path", type=str, default="../config/config.yaml")
    parser.add_argument("--log-path", type=str, default="../logs/kafka_consumer.log")
    parser.add_argument("--env", type=str, default="qas")


    args = parser.parse_args()

    confPath = args.conf_path
    env = args.env
    logPath = args.log_path

    # python kafka_consumer.py
    kafka_massage_consummer_input(confPath, logPath, env)

