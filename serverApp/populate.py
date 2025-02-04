import os
from sqlite3 import IntegrityError
from serverApp.models import User
from serverApp.extensions import db
import pandas as pd

def populate_user_ratings():
    filename = os.getenv("user_ratings_filename", "ratings.csv")
    clean_data(filename)
    with open("ratings_clean.csv", 'r') as f:
        grouped_lines = f.read().split('\n')

    for i in range(1, len(grouped_lines)):
        if grouped_lines[i] != "":

            s = grouped_lines[i]
            ls = s.split(",")
            print(ls)
            user = User(user_id = int(ls[2]), movie_id=ls[3], rating=int(ls[4]))
            print(user)

            try:
                db.session.add(user)
                db.session.commit()
            except IntegrityError:
                db.session.rollback()

def clean_data(filename):
    df = pd.read_csv(filename)
    print(df.shape)
    df.drop_duplicates(subset=["user_id"], keep="first", inplace=True)
    df.drop_duplicates(subset=["movie"], keep="first", inplace=True)
    print(df.shape)
    df.to_csv("ratings_clean.csv")
