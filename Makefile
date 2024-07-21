IMAGES=$(shell docker images -q)
CONTAINERS=$(shell docker ps -q -a)

DB=db
SERVER=model_gen

all: up

up:
	docker-compose up -d

run: up
	docker exec -it $(SERVER) bash

down:
	docker-compose down

view_db: up
	docker exec -it $(DB) psql -d apps_db -U postgres

logs: up
	docker-compose logs

clean: down
	docker-compose rm $(CONTAINERS)
ifneq ($(IMAGES),)
	docker rmi -f $(IMAGES)
endif

rebuild:
	make clean
	make up

.PHONY: run up down view_db logs clean rebuild
