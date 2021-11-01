#!/usr/bin/env python
#coding=utf-8

from aliyunsdkcore.client import AcsClient
from aliyunsdkcore.acs_exception.exceptions import ClientException
from aliyunsdkcore.acs_exception.exceptions import ServerException
from aliyunsdkdcdn.request.v20180115.DescribeDcdnRefreshQuotaRequest import DescribeDcdnRefreshQuotaRequest
import json

def describe_dcdn_refresh_quota(accessKeyId, accessSecret, regionID):
    # 调用DescribeDcdnRefreshQuota查询当日刷新URL、预热URL及刷新目录的上限和剩余次数

    client = AcsClient(accessKeyId, accessSecret, regionID)

    request = DescribeDcdnRefreshQuotaRequest()
    request.set_accept_format('json')

    response = client.do_action_with_exception(request)

    return json.loads(str(response, encoding='utf-8'))

if __name__ == "__main__":
    accessKeyId = "aliyunacesskeyid"
    accessSecret = "aliyunaccesssecret"
    regionID = 'cn-shenzhen'

    print(describe_dcdn_refresh_quota(accessKeyId, accessSecret, regionID))