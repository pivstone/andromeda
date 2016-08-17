#!/bin/bash
VENV=$1
if [ -z $VENV  ]; then
    echo "usage: runinenv [virtualenv_path] CMDS"
    exit 1
fi
. ${VENV}/bin/activate
export DJANGO_SETTINGS_MODULE=andromeda.settings.prodn
shift 1
echo "Executing $@ in ${VENV}"
exec "$@"
deactivate
