#!/usr/bin/env python
#coding=utf-8

from aliyunsdkcore.client import AcsClient
from aliyunsdkcore.acs_exception.exceptions import ClientException
from aliyunsdkcore.acs_exception.exceptions import ServerException
from aliyunsdkdcdn.request.v20180115.PreloadDcdnObjectCachesRequest import PreloadDcdnObjectCachesRequest

client = AcsClient('<accessKeyId>', '<accessSecret>', 'cn-qingdao')

request = PreloadDcdnObjectCachesRequest()
request.set_accept_format('json')

request.set_ObjectPath("web.dearxuany.com.cn/frontend/p__policy__helper__index.a7b54956.async.js")
request.set_Area("domestic")

response = client.do_action_with_exception(request)
# python2:  print(response)
print(str(response, encoding='utf-8'))