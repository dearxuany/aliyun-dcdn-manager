#!/usr/bin/env python
#coding=utf-8

from aliyunsdkcore.client import AcsClient
from aliyunsdkcore.acs_exception.exceptions import ClientException
from aliyunsdkcore.acs_exception.exceptions import ServerException
from aliyunsdkdcdn.request.v20180115.DescribeDcdnRefreshTasksRequest import DescribeDcdnRefreshTasksRequest


def describe_dcdn_refresh_tasks(accessKeyId, accessSecret, regionID):

    client = AcsClient(accessKeyId, accessSecret, regionID)

    request = DescribeDcdnRefreshTasksRequest()
    request.set_accept_format('json')

    response = client.do_action_with_exception(request)
    print(str(response, encoding='utf-8'))

    return str(response, encoding='utf-8')

if __name__ == "__main__":
    accessKeyId = "aliyunacesskeyid"
    accessSecret = "aliyunaccesssecret"
    regionID = 'cn-shenzhen'

    describe_dcdn_refresh_tasks(accessKeyId, accessSecret, regionID)