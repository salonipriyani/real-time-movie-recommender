from flask import Blueprint
import logging

import os
import pandas as pd

# from surprise import Reader, Dataset
# from serverApp.models import User

import json
import numpy as np
from surprise import dump

all_df = pd.read_csv(os.getenv("RATINGS_PATH", "modeling/ratings_clean.csv"))
all_df.drop(['Unnamed: 0.1', 'Unnamed: 0'], axis=1)
all_df = all_df[['user_id', 'movie', 'rating']]
all_df = all_df.rename(columns={"user_id": "user"})
k = 0

recommend_bp = Blueprint('recommend',__name__,url_prefix='/recommend')

# MODEL_DIR = os.path.abspath('models/user-based-algo.dump')
# _, user_algo = dump.load(MODEL_DIR)

SVD_MODEL_DIR = os.path.abspath(os.getenv("MODEL_DUMP_PATH", "modeling/SVD_model.dump"))
_, user_algo2 = dump.load(SVD_MODEL_DIR)


@recommend_bp.route('/<user_id>', methods=['GET'])
def recommend(user_id):
    logging.info('GET /recommend/' + str(user_id))

    try:
        user_id_int = int(user_id)
    except ValueError as ex:
        return "Please enter a valid user id"


    # reader = Reader(rating_scale=(1, 5))
    # all_data = Dataset.load_from_df(all_df[["user", "movie", "rating"]], reader)
    # allset = all_data.build_full_trainset()

    # inner_user_id = allset.to_inner_uid(user_id_int)

    # neighbors = user_algo.get_neighbors(inner_user_id, k=10)

    # all_ratings = list(allset.all_ratings())
    # target_user_ratings = [all_ratings[inner_user_id]]
    # target_user_items = [iid for (uid, iid, r) in target_user_ratings]

    # neighbor_items = []
    # for neighbor in neighbors:
    #     neighbor_ratings = [all_ratings[neighbor]]
    #     for (uid, iid, r) in neighbor_ratings:
    #         neighbor_items.append(iid)

    # unwatched_items = set(neighbor_items) - set(target_user_items)
    # # Predict the ratings for all unwatched items for the given user
    # predictions = [user_algo.predict(user_id_int, allset.to_raw_iid(iid)).est for iid in unwatched_items]

    # predictions_with_item_id = list(zip(unwatched_items, predictions))
    # predictions_with_item_id.sort(key=lambda x: x[1], reverse=True)
    # recommended_items = [(allset.to_raw_iid(item_id), score) for (item_id, score) in predictions_with_item_id]
    recommendString = SVD_model(user_id_int)

    return recommendString

def SVD_model(user_id_int):
        ####### SVD model ##########

    test_user = user_id_int
    df = all_df.copy()
    user_ids = df["user"].unique().tolist()
    user2user_encoded = {x: i for i, x in enumerate(user_ids)}

    movie_ids = df["movie"].unique().tolist()
    movie2movie_encoded = {x: i for i, x in enumerate(movie_ids)}
    movie_encoded2movie = {i: x for i, x in enumerate(movie_ids)}

    df["user"] = df["user"].map(user2user_encoded)
    df["movie_id"] = df["movie"].map(movie2movie_encoded)

    df["rating"] = df["rating"].values.astype(np.float32)
    movies_watched_by_user = df[df.user == test_user]

    # Get movie_id of movies_not_watched
    movies_not_watched = df[~df["movie"].isin(movies_watched_by_user.movie_id.values)]["movie_id"]
    movies_not_watched = list(set(movies_not_watched).intersection(set(movie2movie_encoded.values())))
    # Let the model predict the rating of the movies in movies_not_watched
    ratings = np.array([user_algo2.predict(test_user,movie_encoded2movie[i]).est for i in movies_not_watched])
    # Get the top 20 movies
    top_ratings_indices = ratings.argsort()[-20:][::-1]
    recommended_movies = [(movie_encoded2movie.get(movies_not_watched[x]),ratings[x]) for x in top_ratings_indices]
    recommend = []
    for movie, score in recommended_movies:
        #recommend.append([movie, float(round(score))])
        recommend.append(movie)
    global k
    k += 1
    print(str(k) + " request(s) received")
    recommendString = ','.join(recommend)
    return recommendString
