FROM rabbitmq:management

ENV DEBIAN_FRONTEND noninteractive
ENV DEBCONF_NONINTERACTIVE_SEEN true

ADD ./deployment/rabbitmq/rabbitmq.conf /etc/rabbitmq/

RUN rabbitmq-plugins enable --offline rabbitmq_mqtt rabbitmq_web_mqtt rabbitmq_prometheus rabbitmq_auth_backend_http &&\
    rabbitmq-plugins list