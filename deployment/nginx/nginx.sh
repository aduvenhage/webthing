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
printenv

# complete config and restart
# NOTE: nginx certbot does not modify stream blocks, so we have to manually add it to the config
if [ $AMQP_USE_SSL = True ]
then
    echo "TCP/SSL stream proxy config .. "
    echo "include /etc/nginx/amqp_stream.conf;" >> /etc/nginx/nginx.conf
else
    echo "TCP/no-SSL stream proxy config .. "
    echo "include /etc/nginx/amqp_stream_nossl.conf;" >> /etc/nginx/nginx.conf
fi

service nginx restart

# just wait
sleep infinity

exit 1