#!/bin/bash
# Run this from app deployment folder (on host) -- assumes CWD is webthing/deployment/xxx

export DEPLOY_PATH=$PWD
export ROOT_PATH=$PWD/../..

echo
echo Bash Environment:
printenv

# install basic dependencies
sudo apt update
sudo apt -y upgrade
sudo apt -y install build-essential python-dev python3-pip
pip3 install virtualenv 

# create virtual env
cd $ROOT_PATH
virtualenv venv
. venv/bin/activate

# install app dependencies
pip install -r $DEPLOY_PATH/requirements.txt
deactivate

# install service
sudo cp pycam.service /etc/systemd/system/pycam.service
sudo systemctl enable pycam.service
