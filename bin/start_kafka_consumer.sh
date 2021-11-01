#!/usr/bin/env bash

touch $APP_LOG_PATH/application.log

nohup python src/kafka_consumer.py --conf-path="/root/app/config/config.yaml" --env=$DEPLOY_ENV --log-path="$APP_LOG_PATH/application.log" 2>&1 &

sleep 5
ps -ef|grep kafka_consumer

tail -f $APP_LOG_PATH/application.log