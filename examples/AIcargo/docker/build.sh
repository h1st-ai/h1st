#!/bin/bash

aws ecr get-login-password --region us-west-1 | docker login --username AWS --password-stdin 733647232589.dkr.ecr.us-west-1.amazonaws.com

docker build -t mh_frontend ./h1st_react
docker tag mh_frontend:latest 733647232589.dkr.ecr.us-west-1.amazonaws.com/model_hosting/frontend:latest
docker push 733647232589.dkr.ecr.us-west-1.amazonaws.com/model_hosting/frontend:latest

docker build -t mh_api .
docker tag mh_api:latest 733647232589.dkr.ecr.us-west-1.amazonaws.com/model_hosting/api:latest
docker push 733647232589.dkr.ecr.us-west-1.amazonaws.com/model_hosting/api:latest