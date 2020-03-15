#!/bin/bash

# verify environment variables
echo
echo Bash Environment:
printenv

# verify files in root
echo
echo Root folder content:
ls

# go to source folder
cd ~/webthing

# setup env
export SLACK_TOKEN=xox-

# run app
python pyronix/app.py

exit 1