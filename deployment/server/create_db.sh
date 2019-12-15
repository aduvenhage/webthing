#!/bin/bash

cd $SRC_DEPLOY_PATH
export FLASK_APP=flaskapp/app.py
export FLASK_ENV=development
export FLASK_DEBUG=1

# init DB
flask db init
flask db migrate
flask db upgrade

