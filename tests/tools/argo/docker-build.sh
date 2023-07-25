#!/bin/bash
docker build -t geniadev/backend-production:latest -f backend-production.dockerfile .
docker push geniadev/backend-production:latest

docker build -t geniadev/frontend-production:latest -f frontend-production.dockerfile .
docker push geniadev/frontend-production:latest