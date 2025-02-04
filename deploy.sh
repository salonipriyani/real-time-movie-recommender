#!/bin/bash
set -e
# Erase existing content of .env file
> docker/.env
# produce dump files and ratings.csv files with _$1 argument variable appended to them
pip3 install -r requirements.txt
python3 evaluation/offline/svd_train.py

#update .env file

#Write PIPELINE version using git commit hash
PIPELINE=$(git rev-parse HEAD)
echo "PIPELINE=${PIPELINE}" >> docker/.env

cd docker
#shut down existing processes
docker-compose down

#rebuild and deploy with new models
docker-compose up -d --build
