ENV=$1
FLASK_APP=neomnesis/server/server_main.py
export FLASK_APP=${FLASK_APP}
env_${ENV}/bin/python -m flask run

