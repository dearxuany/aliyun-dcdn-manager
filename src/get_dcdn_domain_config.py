#! /usr/bin/env python
#coding=utf-8

from aliyunsdkcore.client import AcsClient
from aliyunsdkcore.acs_exception.exceptions import ClientException
from aliyunsdkcore.acs_exception.exceptions import ServerException
from aliyunsdkdcdn.request.v20180115.DescribeDcdnDomainConfigsRequest import DescribeDcdnDomainConfigsRequest
import json


def get_dcdn_domain_config(accessKeyId, accessSecret, regionID, domainName, configFuncName):
    # 调用DescribeDcdnDomainConfigs获取加速域名的DCDN配置信息
    client = AcsClient(accessKeyId, accessSecret, regionID)

    request = DescribeDcdnDomainConfigsRequest()
    request.set_accept_format('json')

    request.set_DomainName(domainName)
    request.set_FunctionNames(configFuncName)

    response = client.do_action_with_exception(request)

    domainConfig = json.loads(str(response, encoding='utf-8'))
 
    #print(domainConfig)
    
    return domainConfig


if __name__=="__main__":
    accessKeyId="aliyunacesskeyid"
    accessSecret="aliyunaccesssecret"
    regionID='cn-shenzhen'
    domainName="web.dearxuany.com.cn"
    configFuncName="dynamic"

    get_dcdn_domain_config(accessKeyId, accessSecret, regionID, domainName, configFuncName)
 
