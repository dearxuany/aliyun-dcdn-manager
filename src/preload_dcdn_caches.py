#!/usr/bin/env python
#coding=utf-8

from aliyunsdkcore.client import AcsClient
from aliyunsdkcore.acs_exception.exceptions import ClientException
from aliyunsdkcore.acs_exception.exceptions import ServerException
from aliyunsdkdcdn.request.v20180115.PreloadDcdnObjectCachesRequest import PreloadDcdnObjectCachesRequest


def preload_dcdn_caches(accessKeyId, accessSecret, regionID, objectPath, area):
    # 调用PreloadDcdnObjectCaches将源站的内容主动预热到L2 Cache节点上，用户首次访问可直接命中缓存，缓解源站压力

    client = AcsClient(accessKeyId, accessSecret, regionID)

    request = PreloadDcdnObjectCachesRequest()
    request.set_accept_format('json')

    request.set_ObjectPath(objectPath)
    request.set_Area(area)

    response = client.do_action_with_exception(request)

    print(str(response, encoding='utf-8'))
    return str(response, encoding='utf-8')

if __name__=="__main__":
    accessKeyId="aliyunacesskeyid"
    accessSecret="aliyunaccesssecret"
    regionID='cn-shenzhen'
    objectPath="https://web.dearxuany.com.cn/frontend/static/swiper_img_2.25c56ce6.png"
    area="domestic"

    preload_dcdn_caches(accessKeyId, accessSecret, regionID, objectPath, area)