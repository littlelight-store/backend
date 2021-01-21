#!/usr/bin/env sh

docker-compose -f docker-compose.build-prod.yml build
docker-compose -f docker-compose.build-prod.yml push
