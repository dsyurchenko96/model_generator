IMAGES=$(shell docker images -q)
CONTAINERS=$(shell docker ps -q -a)

DB=db
SERVER=model_gen
TEST_DIR=test

all: run

permissions:
	chmod +x db/001-create-multiple-postgresql-databases.sh

build: permissions
	docker-compose up -d --build

up:
	docker-compose up -d

run: build
	docker exec -it $(SERVER) bash

down:
	docker-compose down

view_db: up
	docker exec -it $(DB) psql -d app -U postgres

test: up
	docker exec -it $(SERVER) pytest -v $(TEST_DIR)

logs: up
	docker-compose logs

clean: down
	docker-compose rm $(CONTAINERS)
ifneq ($(IMAGES),)
	docker rmi -f $(IMAGES)
endif

rebuild:
	make clean
	make build

.PHONY: all build up run down view_db test logs clean rebuild
