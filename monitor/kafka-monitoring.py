from collections import deque

import numpy as np
from kafka import KafkaConsumer
from prometheus_client import Counter, Gauge, Histogram, start_http_server
from sklearn.metrics.pairwise import cosine_similarity

topic = "movielog12"

start_http_server(8765)

# Counter, Gauge, Histogram, Summaries
REQUEST_COUNT = Counter(
    "request_count", "Recommendation Request Count", ["http_status"]
)

REQUEST_LATENCY = Histogram("request_latency_seconds", "Request latency")

PERSONALIZATION_GAUGE = Gauge(
    "personalization_metric", "Personalization Metric", ["window"]
)

SERVICE_HEALTH = Gauge("health_monitor", "Monitor Service Health", ["status"])

class PersonalizationMetric:
    def __init__(self, maxlen=1000):
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


def main():
    personalization_metric = PersonalizationMetric()

    consumer = KafkaConsumer(
        topic,  # topic here
        bootstrap_servers="localhost:9092",
        auto_offset_reset="earliest",
        group_id=topic,  # group ID here
        enable_auto_commit=True,
        auto_commit_interval_ms=1000,
    )

    for message in consumer:
        event = message.value.decode("utf-8")
        values = event.split(",")

        if "recommendation request" in values[2]:
            status = values[3].strip().split(" ")[1]
            REQUEST_COUNT.labels(status).inc()

            time_taken = float(values[-1].strip().split(" ")[0])
            REQUEST_LATENCY.observe(time_taken / 1000)

            personalization_metric.add_response(event)
            personalization_10 = personalization_metric.calculate_personalization_last_n(
                10
            )
            personalization_100 = personalization_metric.calculate_personalization_last_n(
                100
            )
            personalization_1000 = personalization_metric.calculate_personalization()

            is_service_healthy = int(personalization_100 > 0.0)
            SERVICE_HEALTH.labels("Service Healthy").set(is_service_healthy)
            SERVICE_HEALTH.labels("Service Down").set(1 - is_service_healthy)

            PERSONALIZATION_GAUGE.labels("last_10").set(personalization_10)
            PERSONALIZATION_GAUGE.labels("last_100").set(personalization_100)
            PERSONALIZATION_GAUGE.labels("last_1000").set(personalization_1000)


if __name__ == "__main__":
    main()
