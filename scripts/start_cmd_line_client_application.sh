ENV=$1
LOCAL_DIR=`dirname \`readlink -f "$0"\``
NEOMNESIS_DIR="${LOCAL_DIR}/.."
echo ${NEOMNESIS_DIR}
env_${ENV}/bin/python ${NEOMNESIS_DIR}/neomnesis/clients/command_line_client/cmd_client_simple.py 

