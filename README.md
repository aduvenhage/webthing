

## Docker
### RabbitMQ
- `docker build deployment/ -t rabbitmq-web`
- `docker run -d --hostname my-rabbit --name some-rabbit -p 5672:5672 -p 8080:15672 -p 8081:15675 rabbitmq-web`


### Grafana
From `grafana` folder:

- `docker volume create --name=grafana-volume`
- `docker-compose up -d`

