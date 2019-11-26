#!/bin/bash

# verify environment variables
echo
echo Bash Environment:
printenv

# verify files in root
echo
echo Root folder content:
ls

# wait for services to start
echo Waiting on other services ...
sleep 5s

# run server (TODO: run through gunicorn)
cd $SRC_DEPLOY_PATH/flaskapp

export FLASK_APP=main.py
flask run --host=0.0.0.0 --port=5000

# just wait
sleep infinity

exit 1