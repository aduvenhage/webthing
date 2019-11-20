FROM grafana/grafana

ADD ./deployment/grafana/grafana.ini /etc/grafana/
ADD ./deployment/grafana/datasources.yaml /etc/grafana/provisioning/datasources/
ADD ./deployment/grafana/dashboard.yaml /etc/grafana/provisioning/dashboards/
ADD ./deployment/grafana/rabbitmq-overview.json /etc/grafana/provisioning/dashboards/
