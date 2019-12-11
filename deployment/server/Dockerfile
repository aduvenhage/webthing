FROM python:latest

ENV DEBIAN_FRONTEND noninteractive
ENV DEBCONF_NONINTERACTIVE_SEEN true

ARG DEBUG
ARG SRC_DEPLOY_PATH

COPY ./ ${SRC_DEPLOY_PATH}
COPY ./deployment/server/server.sh /server.sh

RUN pip install statsd flask python-dotenv flask-wtf flask-sqlalchemy flask-migrate flask-login flask-bootstrap

