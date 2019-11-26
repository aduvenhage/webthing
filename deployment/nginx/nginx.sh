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

# create HTTPS certificate and port 80 redirects
certbot --nginx --non-interactive --agree-tos --redirect -m $APP_EMAIL --domains $APP_DOMAIN

# complete config and restart
# NOTE: nginx certbot does not modify stream blocks, so we have to manually create it on the domain and add it to the config
#       (see amqp_stream.conf)
echo "include /etc/nginx/amqp_stream.conf;" >> /etc/nginx/nginx.conf
service nginx restart

# just wait
sleep infinity

exit 1