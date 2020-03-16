FROM python:latest

ENV DEBIAN_FRONTEND noninteractive
ENV DEBCONF_NONINTERACTIVE_SEEN true

ARG DEBUG
ARG SRC_DEPLOY_PATH

COPY ./ ${SRC_DEPLOY_PATH}
COPY ./deployment/pyronix/pyronix.sh /pyronix.sh

RUN apt-get update && \
    apt-get -y upgrade && \
    apt-get -y install build-essential python-dev

RUN pip install -r ${SRC_DEPLOY_PATH}/deployment/pyronix/requirements.txt
