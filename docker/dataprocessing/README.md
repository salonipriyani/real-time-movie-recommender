//create recommender network to attach containers to

sudo docker network create recommender

//launch database
docker run --name sqlalchemy-orm-psql \
    -e POSTGRES_PASSWORD=DB_PASSWORD \
    -e POSTGRES_USER=DB_USER \
    -e POSTGRES_DB=sqlalchemy \
    -p 5432:5432 \
    -d postgres \
    --network=recommender

//build the data-processing-app

sudo docker build --tag data-processing-app .

//Launches consumeKafka dara processing docker container, needs recommender network DONT USE

sudo docker run --rm -d --name data-processing-app --network=recommender --add-host=host.docker.internal:host-gateway data-processing-app

//Launches consumeKafka data processing docker container as the host container USE THIS ONE

sudo docker run --rm --name data-processing-app --network=host data-processing-app

//Run Kafka Stream

ssh -L 9092:localhost:9092 tunnel@128.2.204.215 -NTf
