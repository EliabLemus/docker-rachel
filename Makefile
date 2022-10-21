

all: clean build

build: 
	docker build -t registry.gitlab.com/imagenrachelbeta/docker-rachel:latest .
clean:
	docker rm -f rachel
	docker rmi -f registry.gitlab.com/imagenrachelbeta/docker-rachel:latest
	docker system prune -f
