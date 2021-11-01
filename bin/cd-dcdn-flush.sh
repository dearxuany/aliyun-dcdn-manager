#! /bin/bash
. bin/venv_activate.sh
pip install -r requirements.txt
pip list
python src/flush_dcdn.py --conf-path=${Dcdn_Conf_Path} --env=${Deploy_Env} --app-name=${Project_Name}

