#!/bin/bash

export DEPLOY_PATH=$PWD
export ROOT_PATH=$PWD/../../

# install basic dependencies
apt update
apt -y upgrade
apt -y install build-essential python-dev python3-pip
pip3 install virtualenv 

# create virtual env
cd $ROOT_PATH
virtualenv venv
source venv/bin/activate

# install app dependencies
pip install -r $DEPLOY_PATH/requirements.txt
