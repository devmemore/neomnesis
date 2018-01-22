#!/bin/bash
LOCAL_DIR=`dirname $0`
echo "run from $LOCAL_DIR"
bash $LOCAL_DIR/create_venv.sh
source $LOCAL_DIR/.env_local/bin/activate
export FLASK_APP=/usr/local/neomnesis/neomnesis/server/task/server_task.py
$LOCAL_DIR/.env_local/bin/flask run

