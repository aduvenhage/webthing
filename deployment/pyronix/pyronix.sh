
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
cd /home/pi/webthing

# setup env
export DEBUG=True
export PYTHONPATH=.
export SLACK_TOKEN=xoxb +++++ 
. venv/bin/activate


# run app
python pyronix/app.py

# just wait
sleep infinity

exit 1


