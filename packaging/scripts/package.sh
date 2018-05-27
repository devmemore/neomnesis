#!/usr/bin/env bash
LOCAL_DIR=$(dirname $(readlink -f "$0"))
VENV="${LOCAL_DIR}/../../scripts/env_local"
PIP="${VENV}/bin/pip"
PYTHON="${VENV}/bin/python"

${PIP} install pyinstaller

${VENV}/bin/pyinstaller ${LOCAL_DIR}/../../neomnesis/server/server_main.py



