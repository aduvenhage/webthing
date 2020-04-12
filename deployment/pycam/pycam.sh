
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
cd $SRC_DEPLOY_PATH
export PYTHONPATH=$SRC_DEPLOY_PATH

# run app
python pycam/app.py

exit 1


