#!/usr/bin/env python
#coding=utf-8


from aliyunsdkcore.client import AcsClient
from aliyunsdkcore.acs_exception.exceptions import ClientException
from aliyunsdkcore.acs_exception.exceptions import ServerException
from aliyunsdkdcdn.request.v20180115.RefreshDcdnObjectCachesRequest import RefreshDcdnObjectCachesRequest


def dcdn_flush(accessKeyId,accessSecret,regionID,objectPath):

    client = AcsClient(accessKeyId,accessSecret,regionID)


    request = RefreshDcdnObjectCachesRequest()
    request.set_accept_format('json')


    request.set_ObjectPath(objectPath)
    request.set_ObjectType("Directory")


    response = client.do_action_with_exception(request)
    print(str(response, encoding='utf-8'))


if __name__=="__main__":
    accessKeyId="aliyunacesskeyid"
    accessSecret="aliyunaccesssecret"
    regionID='cn-shenzhen'
    objectPath="https://web3.dearxuany.com.cn/"
    
    dcdn_flush(accessKeyId,accessSecret,regionID,objectPath)


