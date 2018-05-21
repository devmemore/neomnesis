ENV=$1
LOCAL_DIR=`dirname \`readlink -f "$0"\``
NEOMNESIS_DIR="${LOCAL_DIR}/.."
cd $NEOMNESIS_DIR
env_${ENV}/bin/python -m neomnesis.clients.command_line_client.cmd_client_simple 
