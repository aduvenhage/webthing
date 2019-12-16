FROM python:latest

ENV DEBIAN_FRONTEND noninteractive
ENV DEBCONF_NONINTERACTIVE_SEEN true

ARG DEBUG
ARG SRC_DEPLOY_PATH

COPY ./ ${SRC_DEPLOY_PATH}
COPY ./deployment/server/server.sh /server.sh

RUN pip install -r ${SRC_DEPLOY_PATH}/deployment/server/requirements.txt

