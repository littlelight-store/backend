#!/usr/bin/env sh

docker build . -t registry.gitlab.com/littlelamplight/littelight-backend:chat-prod
docker push registry.gitlab.com/littlelamplight/littelight-backend:chat-prod

