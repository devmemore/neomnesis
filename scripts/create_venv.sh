MODE=$1

if [ ! -z ${MODE+x} ]; then
    MODE=local
fi

echo $MODE


PYTHON_VERSION="3.6.4"
PYTHON_SOURCE=Python-${PYTHON_VERSION}
PYTHON_BIN=${PYTHON_SOURCE}/python
if [ ! -d "${PYTHON_SOURCE}" ]; then
wget https://www.python.org/ftp/python/${PYTHON_VERSION}/${PYTHON_SOURCE}.tgz 
tar xzf "${PYTHON_SOURCE}.tgz"
echo $(ls -l $LOCAL_DIR)
cd "$LOCAL_DIR/${PYTHON_SOURCE}"
./configure && make
cd ..
fi

VENV="env_${MODE}"
${PYTHON_BIN} -m venv ${VENV}
${VENV}/bin/pip install -r scripts/requirements.txt
