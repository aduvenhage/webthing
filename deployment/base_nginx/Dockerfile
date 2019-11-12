###########################################################################################
#
# Calc UI base -- base image for all docker and gitlab-ci images
#
# USAGE:
# build with: docker build --no-cache -t aduvenhage/nginx-base .
# upload with: docker push aduvenhage/nginx-base
# 
###########################################################################################

FROM nginx:1

ENV DEBIAN_FRONTEND noninteractive
ENV DEBCONF_NONINTERACTIVE_SEEN true

# install Certbot
RUN echo "deb http://deb.debian.org/debian stretch-backports main" | tee -a /etc/apt/sources.list && \
    apt-get update && \
    apt-get -y upgrade && \
    apt-get -y install certbot python-certbot-nginx -t stretch-backports



