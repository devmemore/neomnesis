MODE=local
LOCAL_DIR=`dirname $0`
echo "LOCAL : $LOCAL_DIR"
cd $LOCAL_DIR


if [ ! -z ${MODE+x} ]; then
    MODE=local
fi

echo $MODE


PYTHON_VERSION="3.6.3"
PYTHON_SOURCE=Python-${PYTHON_VERSION}
PYTHON_BIN=${PYTHON_SOURCE}/python
if [ ! -d "${PYTHON_SOURCE}" ]; then
wget https://www.python.org/ftp/python/${PYTHON_VERSION}/${PYTHON_SOURCE}.tgz 
tar xzf "${PYTHON_SOURCE}.tgz"
echo $(ls -l $LOCAL_DIR)
cd "$LOCAL_DIR/${PYTHON_SOURCE}"
./configure && make
fi

VENV="$LOCAL_DIR/.env_${MODE}"
$LOCAL_DIR/${PYTHON_SOURCE}/python -m venv ${VENV}
$VENV/bin/pip install -r requirements.txt
