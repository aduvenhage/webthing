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

# go to source folder
cd $SRC_DEPLOY_PATH

# create DB
sh deployment/flask/create_db.sh

# setup env
export FLASK_APP=webapp/app.py
export FLASK_ENV=development
export FLASK_DEBUG=1

# create user(s)
export PYTHONPATH=$SRC_DEPLOY_PATH
python utils/create_users.py --file deployment/flask/users.json

# run app
flask run --host=0.0.0.0 --port=5000

# just wait
sleep infinity

exit 1