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
sleep 10s

# create HTTPS certificate and port 80 redirect
certbot --nginx --non-interactive --agree-tos --redirect -m $APP_EMAIL --domains $APP_DOMAIN
service nginx start

# nginx should auto start, so just wait
sleep infinity

exit 1