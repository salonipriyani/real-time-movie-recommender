import os
import sys
from collections import deque
from datetime import datetime
from os import path

import numpy as np
from kafka import KafkaConsumer
from sklearn.metrics.pairwise import cosine_similarity
from tqdm import tqdm

maxlen = 1000
telemetry_sample_maxlen = 100


class PersonalizationMetric:
    def __init__(self, maxlen=maxlen):
        self.responses = deque(maxlen=maxlen)

    def add_response(self, response):
        self.responses.append(response)

    def calculate_personalization(self):
        movie_lists = self.extract_movie_recommendations(self.responses)
        binary_matrix = self.create_binary_matrix(movie_lists)
        cosine_sim_matrix = cosine_similarity(binary_matrix)
        personalization = 1 - cosine_sim_matrix
        np.fill_diagonal(personalization, 0)
        return personalization.mean()

    def calculate_personalization_last_n(self, n):
        movie_lists = self.extract_movie_recommendations(self.responses)[-n:]
        binary_matrix = self.create_binary_matrix(movie_lists)
        cosine_sim_matrix = cosine_similarity(binary_matrix)
        personalization = 1 - cosine_sim_matrix
        np.fill_diagonal(personalization, 0)
        return personalization.mean()

    @staticmethod
    def extract_movie_recommendations(responses):
        movie_lists = []
        for response in responses:
            movies = [
                movie.replace("+", " ")
                for movie in response.split(" result: ")[1].split(", ")[:-1]
            ]
            movie_lists.append(movies)
        return movie_lists

    @staticmethod
    def create_binary_matrix(movie_lists):
        all_movies = sorted(set().union(*movie_lists))
        binary_matrix = np.zeros((len(movie_lists), len(all_movies)))

        for i, movies in enumerate(movie_lists):
            for movie in movies:
                binary_matrix[i, all_movies.index(movie)] = 1

        return binary_matrix


def log_personalization_metric(personalization_metric, start_time, log_dir="log"):
    log_file_name = f"{start_time.strftime('%Y-%m-%d_%H-%M-%S')}.log"
    log_path = os.path.join(log_dir, log_file_name)

    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    personalization = personalization_metric.calculate_personalization()

    with open(log_path, "a") as log_file:
        log_file.write(f"{datetime.now()}\tPersonalization: {personalization:.4f}\n")


def capture_response(personalization_metric, pool_size=maxlen):
    cap = pool_size
    count = 0
    total_processed = 0
    start_time = datetime.now()
    telemetry_sample = deque(maxlen=telemetry_sample_maxlen)

    try:
        for message in consumer:
            message = message.value.decode()

            if count < telemetry_sample_maxlen:
                with open("telemetry_sample", "w") as f:
                    for entry in telemetry_sample:
                        f.write(entry + "\n")
            splits = message.split(",")

            if splits[2] == "recommendation request 17645-team12.isri.cmu.edu:8082":
                if count < telemetry_sample_maxlen:
                    telemetry_sample.append(message)
                personalization_metric.add_response(message)
                count += 1
                total_processed += 1

                if count >= cap:
                    count -= 1

                if total_processed % 1000 == 0:
                    log_personalization_metric(personalization_metric, start_time)

                current_time = datetime.now()
                elapsed_time = current_time - start_time
                personalization = personalization_metric.calculate_personalization()
                personalization_10 = personalization_metric.calculate_personalization_last_n(
                    10
                )
                personalization_100 = personalization_metric.calculate_personalization_last_n(
                    100
                )
                sys.stdout.write(
                    f"\033[2K\rStart Time: {start_time}, Current Time: {current_time}, "
                    f"Top {len(personalization_metric.responses)}/{total_processed} processed\n\033[2K\r"
                    f"Personalization (last 10): {personalization_10:.4f}\n\033[2K\r"
                    f"Personalization (last 100): {personalization_100:.4f}\n\033[2K\r"
                    f"Personalization (last 1000): {personalization:.4f}\033[F\033[F\033[F"
                )
                sys.stdout.flush()

    except KeyboardInterrupt:
        print("\nExiting script")
        return personalization_metric.responses


if __name__ == "__main__":
    # create kafka consumer
    topic = "movielog12"
    consumer = KafkaConsumer(
        topic, bootstrap_servers=["localhost:9092"], auto_offset_reset="latest"
    )

    personalization_metric = PersonalizationMetric(maxlen=maxlen)
    responses = capture_response(personalization_metric)
    print(personalization_metric.calculate_personalization())
