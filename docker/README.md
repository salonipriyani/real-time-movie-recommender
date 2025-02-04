#make sure the recommender network exists, and the sqlalchemy-orm-psql is associated with it

sudo docker network ls

sudo docker network inspect recommender

#to create the recommender network and attach sqlalchemy-orm-psql

sudo docker network create recommender

sudo docker network connect recommender sqlalchemy-orm-psql

#to run the experimental service, with load balancing call:

sudo docker-compose up 

#to run the experimental service, with load balancing call, if you've made changes to the containers:

sudo docker-compose up --build 

#to run the same detached:

sudo docker-compose up -d --build

#to spin down

sudo docker-compose down

#export statements for docker-compose
export FEMALE_MODEL=female
export FEMALE_DATA=female
export MALE_MODEL=male
export MALE_DATA=male
export MODEL=meep
export DATA=meep
