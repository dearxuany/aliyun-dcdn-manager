#!/usr/bin/env python
#coding=utf-8

from aliyunsdkcore.client import AcsClient
from aliyunsdkcore.acs_exception.exceptions import ClientException
from aliyunsdkcore.acs_exception.exceptions import ServerException
from aliyunsdkdcdn.request.v20180115.DescribeDcdnRefreshTasksRequest import DescribeDcdnRefreshTasksRequest


def describe_dcdn_refresh_tasks(accessKeyId, accessSecret, regionID,pageNumber,pageSize):
    # 查询刷新、预热状态是否在全网生效，支持查询3天内的数据

    client = AcsClient(accessKeyId, accessSecret, regionID)

    request = DescribeDcdnRefreshTasksRequest()
    request.set_accept_format('json')

    request.set_PageNumber(pageNumber)
    request.set_PageSize(pageSize)

    response = client.do_action_with_exception(request)

    return str(response, encoding='utf-8')


def dcdn_tasks_not_completed(accessKeyId, accessSecret, regionID):
    # aliyun 限制最大操作队列为 100，超过不允许提交，故只需查最新 100 个队列状态即可
    pageSize = 50
    tasksList = []

    for pageNumber in [1,2]:
        result=eval(describe_dcdn_refresh_tasks(accessKeyId, accessSecret, regionID,pageNumber,pageSize))
        tasksList=tasksList+result["Tasks"]["Task"]


    tasksNotCompleted=[]
    for n in range(0,len(tasksList)):
        if tasksList[n]['Status'] != "Complete":
            tasksNotCompleted.append(tasksList[n])

    return tasksNotCompleted








if __name__ == "__main__":
    accessKeyId = "aliyunacesskeyid"
    accessSecret = "aliyunaccesssecret"
    regionID = 'cn-shenzhen'

    print(dcdn_tasks_not_completed(accessKeyId, accessSecret, regionID))
