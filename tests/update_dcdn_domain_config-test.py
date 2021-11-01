#!/usr/bin/env python
#coding=utf-8

from aliyunsdkcore.client import AcsClient
from aliyunsdkcore.acs_exception.exceptions import ClientException
from aliyunsdkcore.acs_exception.exceptions import ServerException
from aliyunsdkdcdn.request.v20180115.BatchSetDcdnDomainConfigsRequest import BatchSetDcdnDomainConfigsRequest


def update_dcdn_domain_config(accessKeyId, accessSecret, regionID, domainName, functionsInput):

    print(type(str(functionsInput)))
    print(str(functionsInput))

    client = AcsClient(accessKeyId, accessSecret, regionID)

    request = BatchSetDcdnDomainConfigsRequest()
    request.set_accept_format('json')

    request.set_DomainNames(domainName)

    request.set_Functions(str(functionsInput))

    response = client.do_action_with_exception(request)

    print(str(response, encoding='utf-8'))


if __name__=="__main__":
    accessKeyId="aliyunacesskeyid"
    accessSecret="aliyunaccesssecret"
    regionID='cn-shenzhen'
    domainName="web3.dearxuany.com.cn"
    functionsInput=[{"functionArgs":[{"argName":"enable","argValue":"on"},{"argName":"static_route_path","argValue":"/frontend/static/* /frontend/js/* /images/* /product/static/* /test/batch/set/*"}],"functionName":"dynamic","configId":146031169437697}]

    update_dcdn_domain_config(accessKeyId, accessSecret, regionID, domainName, functionsInput)