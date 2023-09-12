#!/bin/bash

docker compose build
docker compose push
yes | docker image prune
docker images
