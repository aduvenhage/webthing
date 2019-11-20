

# Docker
The `docker-compose.yaml` and `.env` files are in the source folder root.  Container images are built on base images (uploaded to dockerhub), to make deployment as quick as possible.  Containers communicate using docker network names.
`.env` file is used for both build time and runtime variables.

### Install docker-compose (Linux / Ubuntu / Cloud VM)
Locally
```
sudo apt-get install curl docker.io
sudo curl -L "https://github.com/docker/compose/releases/download/1.23.1/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
sudo usermod -a -G docker $USER
```
**IMPORTANT**: Next, log out and in again in order for user-group permissions to be applied.

Inside container
```
curl -L "https://github.com/docker/compose/releases/download/1.24.1/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose
```

### Install Docker Machine
Install docker-machine: https://docs.docker.com/machine/install-machine/
  ```
  base=https://github.com/docker/machine/releases/download/v0.16.0 && curl -L $base/docker-machine-$(uname -s)-$(uname -m) >/tmp/docker-machine && sudo mv /tmp/docker-machine /usr/local/bin/docker-machine && chmod +x /usr/local/bin/docker-machine
  ```

### Docker Commands
- list all containers: `docker ps`
- exec into container: `docker exec -ti CONRAINER_ID bash`
- kill all containers: `docker kill $(docker ps -q)`
- delete all stopped containers: `docker rm $(docker ps -a -q)`
- delete all images: `docker rmi $(docker images -q)`

### Docker machine commands
- create VM (ubuntu 18.04 LTS -- Digital Ocean): 
  ```
  docker-machine create --driver digitalocean --digitalocean-image ubuntu-18-04-x64 --digitalocean-region sfo2 --digitalocean-access-token=1aa8b56892d2e8bfc9c4d0a1c55c09109b6fdc8d9ab2e2c26519289c7ed07624 mysmarthome
  ```
- activate docker env: `eval $(docker-machine env mysmarthome) .`
- deactivate docker env: `eval $(docker-machine env -u)`
- ssh into remote machine: `docker-machine ssh mysmarthome`
- list machines: `docker-machine ls`
- remove machines: `docker-machine rm mysmarthome`
- provision a system: docker-machine (create --> ssh --> docker-compose up)

- NOTE: Docker containers may not use volumes/shares/mounts. All shared data must be copied from Dockerfiles
- NOTE: Digital Ocean VMs have to be in the same data center (in this case sfo2) as their floating IPs


### Exec into Containers
- **Prometheus**: docker-compose exec prometheus /bin/sh
- **RabbitMQ**: docker-compose exec rabbitmq bash
