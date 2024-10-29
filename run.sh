#!/bin/bash
# Stop and remove all containers, networks, and volumes created by docker-compose
docker-compose down --volumes --remove-orphans

# Rebuild and restart all services as defined in docker-compose.yml
docker-compose up --build