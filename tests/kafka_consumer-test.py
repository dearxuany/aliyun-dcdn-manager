from kafka import KafkaConsumer
import json

consumer = KafkaConsumer('dev_aliyun-dcdn-preload', group_id= 'liyunxuan-test', bootstrap_servers= ['10.0.0.50:9092'])

for msg in consumer:
    print(msg)
    print(type(msg.value))
    a=msg.value.decode()
    print(a)
    print(type(a))