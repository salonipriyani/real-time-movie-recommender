//build the flask-app

sudo docker build --tag flask-exp --build-arg female_model=FEMALE --build-arg female_data=FEMALE --build-arg male_model=MALE --build-arg male_data=MALE --build-arg pipeline=PIPE .

//Launches flask-app container, needs recommender network

sudo docker run --rm -d --name flask-exp --network=recommender -p 8082:8082 flask-exp
