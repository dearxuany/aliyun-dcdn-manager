# aliyun-dcdn-manager
阿里云 全站加速 DCDN 管理脚本
## 项目描述
主要用于前端应用版本更新所需的全站加速 DCDN 刷新、预热自动化处理，由 jenkins 于 CD 完成 k8s 新版本代码部署时触发。
## 前置准备
前端应用打包及文件列表生成命令，配置于 jenkins 各个项目 CI 第一步，需要使用 jenkins 的 build_num 作为文件列表名称的后缀，以区分版本。
```
cd $WORKSPACE
/usr/local/bin/npm install
/usr/local/bin/npm run build
ls -alS dist/ > frontend_file_list.log
find dist >> frontend_file_list.log
cp -a frontend_file_list.log /sdata/data/aliyun-dcdn-manager/frontend-file-list/${Project_Name}-build_$BUILD_NUMBER
tar -zcf app.gz dist/
```
jenkins CD 触发脚本
```
echo -e "\n查看WORKSPACE文件:\n "
ls -al

echo -e "\n打印部署脚本:\n"
cat cd-helm-deploy/cd-prd.sh

echo -e "\n上次部署镜像版本:\n"
lastOnlineVersion=$(kubectl get pods -n ${Prd_NameSpace} -o=jsonpath="{..image}" -l app=${Project_Name} --kubeconfig prd-admin.kubeconfig |tr -s '[[:space:]]' '\n'|sort|uniq)
echo "lastOnlineVersion=$lastOnlineVersion" > ./parameters.tmp
cat ./parameters.tmp

echo -e "\n开始执行部署脚本:\n"
sh cd-helm-deploy/cd-prd.sh

echo -e "\n开始执行 DCDN 刷新:\n"
echo -e ${Dcdn_Conf_Path} ${Deploy_Env} ${Project_Name} $lastOnlineVersion
cd aliyun-dcdn-manager && sh bin/cd-dcdn-multi-actions.sh
```
## 项目结构
```
# tree -L 3
.
├── bin
│   ├── cd-dcdn-flush.sh                                # DCDN 域名刷新触发脚本
│   ├── cd-dcdn-multi-actions.sh                        # 包含 DCDN 域名刷新、预热触发脚本，现主要使用的脚本
│   ├── clean_old_frontend_file_list.sh                 # 应用文件列表数据清理脚本
│   ├── start_kafka_consumer.sh                         # kafka 消费者启动脚本，主要用于缓存预热请求队列
│   ├── venv_activate.sh                                # 虚拟环境激活
│   └── venv_create.sh                                  # 创建虚拟环境
├── config
│   └── config.yaml                                     # 项目配置文件
├── data                                                
│   └── frontend-file-list-example                      # jenkins 更版时生成的前端应用静态资源列表样例
│       ├── dearxuany-front-build_293                     # 实际存储路径可在 --app-file-info-path 自定义
│       ├── dearxuany-front-h5-build_766        # 文件名格式为“jenkins项目名称-build_jenkins构建号”
│       ├── dearxuany-front-h5-build_767
│       └── dearxuany-front-h5-build_768
├── docs
│   ├── dataformat
│   ├── websocket_curl.sh                               # websocket 调试脚本
│   └── websocket_ws_test.html
├── README.md
├── requirements.txt                                    # python 依赖包
├── src                                                 # 项目源码
│   ├── compare_dcdn_config_with_new_app.py             # 已在使用在阿里云控制台配置的静态文件类型后缀替代，用于区分动静态资源
│   ├── compare_file_list_with_old_app.py               # 对比新旧两个版本应用静态资源列表，获取应用新版本新增的文件列表用于预热，使用URL文件刷新时用到
│   ├── config.py                                       # 配置读取模块
│   ├── describe_dcdn_refresh_quota.py                  # 阿里云 DCDN 刷新预热当天上限余量查询 API DescribeDcdnRefreshQuota
│   ├── describe_dcdn_refresh_tasks.py                  # 阿里云 DCDN 刷新预热任务完成进度查询 API DescribeDcdnRefreshTasks
│   ├── flush_dcdn.py                                   # DCDN 刷新入口
│   ├── get_app_common_value.py                         # 随机 12 个版本对比获取应用 app 同名的静态资源，主要用于长期同名静态文件刷新，使用目录刷新不需要
│   ├── get_dcdn_domain_config.py                       # 阿里云查询指定域名 DCDN 配置 API DescribeDcdnDomainConfigs
│   ├── get_frontend_file_info_list.py                  # 将应用项目静态资源文件列表转换为 URI 字典，静态文件列表来源于 --app-file-info-path
│   ├── __init__.py
│   ├── kafka_consumer.py                               # DCDN 预热请求 kafka 队列消费者
│   ├── kafka_producer.py                               # DCDN 预热请求 kafka 队列生产者
│   ├── logging_set.py                                  # 日志管理模块
│   ├── preload_dcdn_caches.py                          # 阿里云 DCDN 预热 API PreloadDcdnObjectCaches 
│   ├── preload_dcdn_caches_with_new_app.py             # DCDN 预热入口
│   └── read_file.py                                    # 文件读取模块
└── tests                                               # 模块测试代码
    ├── argparse_config_input-test.py
    ├── config-test.py
    ├── describe_dcdn_refresh_quota-test.py
    ├── describe_dcd_refresh_tasks-tests.py
    ├── flush_dcdn-test.py
    ├── get_comm_value-test.py
    ├── get_dcdn_domain_config-test.py
    ├── __init__.py
    ├── kafka_consumer-test.py
    ├── kafka_producer-test.py
    ├── preload_dcdn_caches-test.py
    └── update_dcdn_domain_config-test.py
```
## 配置项及功能
### 启动参数
启动传入配置可于触发脚本 bin 目录中两个 cd 脚本中配置，参数可在 jenkins 中以环境参数传入，也可直接配置。
```
--conf-path=${Dcdn_Conf_Path}                                                   # 配置文件路径，默认值为 "../config/config.yaml"
--env=${Deploy_Env}                                                             # 环境参数，对应配置文件 yaml 中 key
--app-name=${Project_Name}                                                      # 前端应用项目名称                               
--app-build-num=${DockerImageTag}                                               # jenkins 构建号，主要用于区分应用文件列表版本
--app-file-info-path="/sdata/data/aliyun-dcdn-manager/frontend-file-list"       # 前端应用静态资源列表生成目录
--log-path="/sdata/var/log/aliyun-dcdn-manager/application.log"                 # 日志路径
--last-app-build-num=$lastAppBuildNum                                           # 当前在线应用版本号（即更新前版本号）
--preload-way="all"                                                             # DCDN 预热方式
```
其中 --preload-way 配置项较为特殊，该配置项控制 DCDN 的预热方式：
设置为 all 时为全量文件预热，需将 DCDN 刷新方式设置为 Directory 配合使用，刷新预热整个域名指定目录下所有文件；
默认值为 update 仅预热已变更过的文件，需要将 DCDN 刷新方式设置为 File 配合使用，仅刷新预热更新过的文件。
因项目 url 跳转形式的配置限制，现必须使用全量文件刷新预热，故需设置 --preload-way="all"，同时在配置文件中将 flushType 设置为 Directory。
### 配置参数
配置文件默认位置，格式为 yaml，以 key-value 形式支持多环境配置，环境选择对应启动参数 --env=${Deploy_Env}
```
config/config.yaml
```
配置文件现按实际区分 dev、qas、uat、prd。
dev 环境由于没有 DCDN 故无需配置留空，uat 环境由于与 prd 共用域名故禁止配置刷新预热，否则会将未达到上线标准的 uat 版本静态资源文件缓存到 DCDN 上造成生成故障。
配置文件内容样例如下所示：
```
dev:
  env: dev


qas:                                                            # 环境名称
  env: qas
  accessKeyId: aliyunaccesskeyid                                # 阿里云鉴权 accessKeyId
  accessSecret: aliyunaccesssecret                              # 阿里云鉴权 accessSecret
  regionID: cn-shenzhen                                         # 阿里云 DCDN 所在区域
  waitTimeBeforeFlush: 60                                       # 前端应用新旧容器版本切换完成前置等待时间，防止 DCDN 预热请求到旧版本应用容器
  waitTimeBeforePreload: 10                                     # DCDN 预热前置等待时间，防止 DCDN 未完成刷新就启动预热
  preloadMQUse: kafka                                           # DCDN 预热队列缓存 kafka 开关，仅当值为 kafka 时程序将预热队列消息发动给 kafka 再通过消费者发送预热请求到 DCDN，其他值均默认为直接发送预热请求到 DCDN 可能导致预热队列阻塞或公网入口IP丢包，建议使用 kafka
  kafkaServer: 10.0.0.50:9092                                   # kafka 链接地址及端口，多个节点使用英文逗号隔开
  kafkaTopic: qas_aliyun-dcdn-preload                           # kafka 消息 topic
  kafkaGroupID: qas_aliyun-dcdn-manager-preload                 # kafka 消费者组
  application:                                                  # application 通过应用项目名称划分，严格对照 jenkins 传入的 --app-name 参数
    full-station:                                               # 当 --app-name="full-station" 不区分应用项目选项，默认配置为刷新域名根目录用
      web3.dearxuany.com.cn:                                   # full-station 下 DCDN 目标处理域名1
        enable: False                                           # 是否开启当前域名配置项，为 True 时开启当前域名 DCDN 刷新功能
        protocol: http,https                                    # DCDN 刷新协议，多个协议逗号隔开，http 及 https 分开计算，故最好两个都填，同时开启 http 和 https 刷新
        flushType: Directory                                    # DCDN 刷新方式，Directory 为目录刷新，File 为指定文件刷新
        flushPath: /                                            # DCDN 域名刷新指定下级目录路径
      web.dearxuany.com.cn:                                    # full-station 下 DCDN 目标处理域名2与指定域名1同时按配置触发刷新，可类推添加多个域名
        enable: True                                         
        protocol: http,https
        flushType: Directory
        flushPath: /
    dearxuany-front-h5:                                 # 启动参数 --app-name 指定应用项目名，单个项目根据实际代理情况，可同时指定多个需刷新预热的域名
      web3.dearxuany.com.cn:
        enable: True
        protocol: http,https        
        flushType: Directory
        flushPath: /front                                       # 应用项目在此域名下对应的 url 访问目录前缀，flushType 为 Directory 时使用
        flushURI: js/matomo.js,index.html                       # 应用项目指定需要每次刷新的文件，flushType 为 File 时使用
        preload: disable                                        # 域名预热开关，为 enable 时开启该域名预热功能
        preloadProtocol: https                                  # 域名预热协议，多个逗号分隔，由于 http 比较少人用，为节省预热额度仅预热 https 资源
      web.dearxuany.com.cn:
        enable: True
        protocol: http,https
        flushType: Directory
        flushPath: /front
        flushURI: js/matomo.js,index.html
        preload: disable
        preloadProtocol: https
    dearxuany-front:
      web3.dearxuany.com.cn:
        enable: False
        protocol: http,https
        flushType: File
        flushPath: /product
        flushURI: index.html
        preload: disable
        preloadProtocol: https
      web.dearxuany.com.cn:
        enable: True
        protocol: http,https
        flushType: Directory
        flushPath: /product
        flushURI: index.html
        preload: disable
        preloadProtocol: https


uat:
  env: uat


prd:
  env: prd
  accessKeyId: aliyunaccesskeyid
  accessSecret: aliyunaccesssecret
  regionID: cn-shenzhen
  waitTimeBeforeFlush: 60
  waitTimeBeforePreload: 10
  preloadMQUse: kafka
  kafkaServer: 192.16.40.110:9092,192.16.40.111:9092,192.16.40.112:9092
  kafkaTopic: prd_aliyun-dcdn-preload
  kafkaGroupID: prd_aliyun-dcdn-manager-preload
  application:
    full-station:
      web.dearxuany.com:
        enable: True
        protocol: http,https
        flushType: Directory
        flushPath: /
    dearxuany-front-h5:
      web.dearxuany.com:
        enable: True
        protocol: http,https
        flushType: Directory
        flushPath: /front
        flushURI: js/matomo.js,index.html,js/nim/NIM_Web_SDK_v.js
        preload: enable
        preloadProtocol: https
    dearxuany-front:
      web.dearxuany.com:
        enable: True
        protocol: http,https
        flushType: Directory
        flushPath: /product
        flushURI: index.html
        preload: enable
        preloadProtocol: https

```