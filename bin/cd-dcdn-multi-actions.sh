#! /bin/bash
. bin/venv_activate.sh
pip install -r requirements.txt
pip list

lastAppBuildNum=$(cat ../parameters.tmp|grep lastOnlineVersion | cut -d ":" -f 2)
echo $lastAppBuildNum

#echo $(date) "等待 60 秒，等待 k8s 前端新版容器切换完毕"
#sleep 60
#echo $(date) "等待结束，开始刷新 DCDN"
python src/flush_dcdn.py --conf-path=${Dcdn_Conf_Path} --env=${Deploy_Env} --app-name=${Project_Name}
#python src/compare_dcdn_config_with_new_app.py --conf-path=${Dcdn_Conf_Path} --env=${Deploy_Env} --app-name=${Project_Name} --app-build-num=${DockerImageTag} --app-file-info-path="/sdata/data/aliyun-dcdn-manager/frontend-file-list" --log-path="/sdata/var/log/aliyun-dcdn-manager/application.log"

echo $(date) "等待 10 秒，等待 DCDN 域名目录刷新完成"
sleep 10
echo $(date) "等待结束，开始预热 URL"
python src/preload_dcdn_caches_with_new_app.py --preload-way="all" --conf-path=${Dcdn_Conf_Path} --env=${Deploy_Env} --app-name=${Project_Name} --app-build-num=${DockerImageTag} --app-file-info-path="/sdata/data/aliyun-dcdn-manager/frontend-file-list" --log-path="/sdata/var/log/aliyun-dcdn-manager/application.log" --last-app-build-num=$lastAppBuildNum