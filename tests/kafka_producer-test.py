from kafka import KafkaProducer
from kafka.errors import KafkaError
import json

# 发送成功的回调函数
def on_send_success(record_metadata):
    print(record_metadata.topic)
    print(record_metadata.partition)
    print(record_metadata.offset)


# 发送失败的回调函数
def on_send_error(excp):
    log.error('I am an errback', exc_info=excp)
    # handle exception


def kafka_massage_send(kafkaServer,kafkaTopic,kafkaSendMsgRetriesTimes,kafkaSendMsg):

    # 发送json格式消息
    kafkaMsgType=lambda m: json.dumps(m).encode('ascii')

    producer = KafkaProducer(bootstrap_servers=kafkaServer,retries=kafkaSendMsgRetriesTimes,value_serializer=kafkaMsgType)

    # 带有回调函数的异步发送
    request = producer.send(kafkaTopic, kafkaSendMsg).add_callback(on_send_success).add_errback(on_send_error)

    # 异步发送模块
    try:
        record_metadata = request.get(timeout=10)
    except KafkaError:
        # Decide what to do if produce request failed...
        log.exception()
        pass


if __name__=="__main__":
    kafkaServer=['10.0.0.50:9092']
    kafkaSendMsgRetriesTimes=5
    kafkaTopic='dev_aliyun-dcdn-preload'
    kafkaSendMsg={"key":"value"}

    kafka_massage_send(kafkaServer, kafkaTopic, kafkaSendMsgRetriesTimes, kafkaSendMsg)