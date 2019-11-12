FROM rabbitmq:management

ENV DEBIAN_FRONTEND noninteractive
ENV DEBCONF_NONINTERACTIVE_SEEN true

RUN rabbitmq-plugins enable --offline rabbitmq_mqtt rabbitmq_web_mqtt