IMAGES=$(shell docker images -q)
CONTAINERS=$(shell docker ps -q -a)

DB=db
SERVER=model_gen

all: up

up: permissions
	docker-compose up -d

permissions:
	chmod +x db/001-create-multiple-postgresql-databases.sh

run: up
	docker exec -it $(SERVER) bash

down:
	docker-compose down

view_db: up
	docker exec -it $(DB) psql -d app -U postgres

view_test_db: up
	docker exec -it $(DB) psql -d app_test -U postgres

test: up
	docker exec -it $(SERVER) pytest -v -s test/

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
