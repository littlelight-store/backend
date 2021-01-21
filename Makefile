
build:
	$(info Make: build development docker-compose)
	@docker-compose build --pull

push:
	$(info Make: Starting development docker-compose)
	@docker-compose push

deploy:
	$(info Make: Starting development docker-compose)
	@docker-compose build --pull
	@docker-compose push
