
#!/bin/bash

# verify environment variables
echo
echo Bash Environment:
printenv

# run app
export PYTHONPATH=$PWD
python pycam/app.py
