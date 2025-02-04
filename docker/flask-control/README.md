//build the flask-app

sudo docker build --tag flask-control --build-arg model=MEEP --build-arg data=MEEP --build-arg pipeline=PIPE .

//Launches flask-app container, needs recommender network

sudo docker run --rm -d --name flask-control --network=recommender -p 8082:8082 flask-control

sudo docker run --rm --name flask-control --network=recommender -p 5001:5001 flask-control

