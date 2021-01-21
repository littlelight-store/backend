#!/usr/bin/env sh

docker-compose -f docker-compose.build-stage.yml build
docker-compose -f docker-compose.build-stage.yml push
