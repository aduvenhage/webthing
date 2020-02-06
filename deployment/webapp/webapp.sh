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
sh deployment/webapp/create_db.sh

# setup env
export FLASK_APP=webapp/app.py
export FLASK_ENV=development
export FLASK_DEBUG=1

# create user(s)
export PYTHONPATH=$SRC_DEPLOY_PATH
python utils/create_users.py --file deployment/webapp/users.json

# run app
#flask run --host=0.0.0.0 --port=5000
#uwsgi -H venv/ --die-on-term --socket 0.0.0.0:5000 --protocol=http --module webapp.wsgi:app
uwsgi -H venv/ --ini $SRC_DEPLOY_PATH/config.ini

# just wait
sleep infinity

exit 1