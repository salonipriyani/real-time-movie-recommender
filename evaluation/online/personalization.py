import os
import sys
from os import path

import numpy as np
from kafka import KafkaConsumer
from sklearn.metrics.pairwise import cosine_similarity
from tqdm import tqdm


def extract_movie_recommendations(responses):
    movie_lists = []
    for response in responses:
        movies = [
            movie.replace("+", " ")
            for movie in response.split(" result: ")[1].split(", ")[:-1]
        ]
        movie_lists.append(movies)
    return movie_lists


def create_binary_matrix(movie_lists):
    all_movies = sorted(set().union(*movie_lists))
    binary_matrix = np.zeros((len(movie_lists), len(all_movies)))

    for i, movies in enumerate(movie_lists):
        for movie in movies:
            binary_matrix[i, all_movies.index(movie)] = 1

    return binary_matrix


def calculate_personalization(responses):
    movie_lists = extract_movie_recommendations(responses)
    binary_matrix = create_binary_matrix(movie_lists)
    cosine_sim_matrix = cosine_similarity(binary_matrix)
    personalization = 1 - cosine_sim_matrix
    np.fill_diagonal(personalization, 0)
    return personalization.mean()


def capture_response(pool_size=100):
    cap = pool_size
    count = 0
    responses = []
    for message in tqdm(consumer):
        if count > cap:
            break
        message = message.value.decode()
        splits = message.split(",")
        # print(splits)

        if splits[2] == "recommendation request 17645-team12.isri.cmu.edu:8082":
            # print(splits)
            # print(message)
            responses.append(message)
            count += 1

    return responses


if __name__ == "__main__":
    # create kafka consumer
    topic = "movielog12"
    consumer = KafkaConsumer(
        topic,
        bootstrap_servers=["localhost:9092"],
        auto_offset_reset="latest",
    )

    responses = capture_response()
    print(calculate_personalization(responses))
