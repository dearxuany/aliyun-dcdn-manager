#! /bin/sh

location="/sdata/data/aliyun-dcdn-manager/frontend-file-list"

find $location -mtime +30 -type f -name *build* |xargs rm -f
