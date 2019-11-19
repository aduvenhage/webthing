# custom base image (see deployment/base_nginx/Dockerfile)
FROM arnoduvenhage/nginx-base

ENV DEBIAN_FRONTEND noninteractive
ENV DEBCONF_NONINTERACTIVE_SEEN true
USER root

# move required files
COPY ./deployment/nginx/nginx.conf /etc/nginx/nginx.conf
COPY ./deployment/nginx/amqp_stream.conf /etc/nginx/amqp_stream.conf
COPY ./deployment/nginx/nginx.sh /nginx.sh


