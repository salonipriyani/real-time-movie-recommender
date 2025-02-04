import argparse
import pandas as pd
from collections import defaultdict

def parse_recommendation_request_telemetry(telemetry_data):
    recommendation_requests = []

    for line in telemetry_data.split("\n"):
        if "recommendation request" in line:
            recommendation_requests.append(line)

    return recommendation_requests

def extract_movie_recommendations(recommendation_requests):
    movie_lists = []
    for request in recommendation_requests:
        movies = [
            movie.replace("+", " ")
            for movie in request.split(" result: ")[1].split(", ")[:-1]
        ]
        movie_lists.append(movies)
    return movie_lists

def calculate_average_rating(rating_data):
    rating_data["movie"] = rating_data["movie"].str.replace("+", " ")  # Replace '+' with spaces
    rating_data["rating"] = rating_data["rating"].astype(float)
    avg_rating = rating_data.groupby("movie")["rating"].mean().reset_index()
    avg_rating.columns = ["movie", "average_rating"]
    return avg_rating

def merge_recommendation_and_rating_data(recommendation_data, avg_rating):
    movie_counts = defaultdict(int)

    for movie_list in recommendation_data:
        for movie in movie_list:
            movie_counts[movie] += 1

    recommendation_count_data = pd.DataFrame(
        movie_counts.items(), columns=["movie", "recommendation_count"]
    )

    merged_data = pd.merge(
        recommendation_count_data, avg_rating, on="movie", how="left"
    )  # Use left join

    return merged_data

def main(args):
    with open(args.input, "r") as f:
        telemetry_data = f.read()

    recommendation_requests = parse_recommendation_request_telemetry(telemetry_data)
    recommendation_data = extract_movie_recommendations(recommendation_requests)

    rating_data = pd.read_csv("ratings.csv")
    avg_rating = calculate_average_rating(rating_data)
    merged_data = merge_recommendation_and_rating_data(recommendation_data, avg_rating)

    merged_data = merged_data.dropna()  # Drop rows with missing ratings
    numeric_columns = merged_data.select_dtypes(include=['number'])  # Select numeric columns
    correlation = numeric_columns.corr().loc["average_rating", "recommendation_count"]

    print(f"Correlation between average ratings and recommendation count: {correlation}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Analyze feedback loop in movie recommendation system."
    )
    parser.add_argument(
        "-i",
        "--input",
        type=str,
        required=True,
        help="Path to the telemetry data file containing recommendation requests.",
    )
    args = parser.parse_args()
    main(args)
