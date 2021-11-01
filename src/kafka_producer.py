from kafka import KafkaProducer
from kafka.errors import KafkaError
import json


def kafka_producer_massage_clean(type,timeStrftime,msgID,rawData):
    if type == "dcdnPreload":
        data={"timeStrftime":timeStrftime,"msgType":type,"msgID":msgID,"requestObjectStr":rawData}

    return data


# 发送成功的回调函数
def on_send_success(record_metadata):
    print("kafka 消息发送正常 topic: {} partition: {} offset: {}".format(record_metadata.topic,record_metadata.partition,record_metadata.offset))
    return True


# 发送失败的回调函数
def on_send_error(excp):
    print("kafka 消息发送异常 {}".format(excp))
    #log.error('I am an errback', exc_info=excp)
    return False


def kafka_massage_send(kafkaServer, kafkaTopic, kafkaSendMsg):

    # 发送json格式消息
    kafkaMsgType=lambda m: json.dumps(m).encode('ascii')

    producer = KafkaProducer(bootstrap_servers=kafkaServer,retries=3,value_serializer=kafkaMsgType)

    # 带有回调函数的异步发送
    request = producer.send(kafkaTopic, kafkaSendMsg).add_callback(on_send_success).add_errback(on_send_error)

    # 异步发送模块
    try:
        record_metadata = request.get(timeout=10)
    except KafkaError:
        # Decide what to do if produce request failed...
        log.exception()
        pass

    return request

if __name__=="__main__":
    kafkaServer=['10.0.0.50:9092']
    kafkaTopic='dev_aliyun-dcdn-preload'
    kafkaSendMsg={"key":"value"}

    kafka_massage_send(kafkaServer, kafkaTopic ,kafkaSendMsg)