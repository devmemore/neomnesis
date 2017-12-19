MODE=$1

if [ ! -z ${MODE+x} ]; then
    MODE=local
fi

echo $MODE


PYTHON_VERSION="3.6.3"
PYTHON_SOURCE=Python-${PYTHON_VERSION}
PYTHON_BIN=${PYTHON_SOURCE}/python
if [ ! -d "${PYTHON_SOURCE}" ]; then
wget https://www.python.org/ftp/python/${PYTHON_VERSION}/${PYTHON_SOURCE}.tgz
tar xzf ${PYTHON_SOURCE}.tgz
cd ${PYTHON_SOURCE}
./configure && make
fi

VENV=".env_${MODE}"
${PYTHON_BIN} -m venv ${VENV}
source "${VENV}/bin/activate"
pip install -r requirements.txt
