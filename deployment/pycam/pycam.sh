
#!/bin/bash
# Run this from source root folder -- assumes CWD is webthing (source route)

echo
echo Bash Environment:
printenv

# run app
export PYTHONPATH=$PWD
python pycam/app.py
