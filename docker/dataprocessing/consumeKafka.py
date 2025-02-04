from kafka import KafkaConsumer, KafkaProducer
import os

from datetime import date
from datetime import datetime
from dateutil.relativedelta import relativedelta

from sqlite3 import IntegrityError

#import sys
#sys.path.append("..")dataprocessing.

from base import Session, engine, Base
from models import Rating, RatingAverage
from sqlalchemy.dialects.postgresql import insert


TOPIC_NAME = "movielog12"

KAFKA_SERVER = "localhost:9092"

#KAFKA_SERVER = "172.17.0.1:9092"

CURRENT_YEAR = date.today().year
FIRST_MOVIE_YEAR = 1891

movies = {}

RATINGS_COUNT = 0
AVERAGE_RATING = 0
WINDOW_OF_AVERAGE_RATINGS = 100


def valid_movie_year(year):
    if year and year.isdigit():
        year = int(year)
        if year >= FIRST_MOVIE_YEAR and year <= CURRENT_YEAR:
          return True

    return False


def processRating(data, user, timestamp, DEBUG = False):
    titleLen = len(data)
    movie = data[:titleLen-2]
    validated = True

    #RATING VERIFICATION
    try:
        rating = int(data[titleLen-1:])

    except:
        print(f"Error: rating {data[2][titleLen-1:]} must be an integer")
        return False

    if rating not in range(0,6):
        print(f"Error: rating outside of accepted range!: {rating}")
        return False

    elif movie not in movies:
        #MOVIE VERIFICATION
        if not valid_movie_year(movie[-4:]):
            print(f"Error: {movie[-4:]} is not a valid year for {movie}")
            validated = False
        else:
            movies[movie] = 1

            if not DEBUG:
                updateRating(user, movie, rating, timestamp);

            #print(f"New rating by user {user} for {movie}: {rating}")
            #print(f"{movie} has been rated {movies[movie]} times")
    else:
        movies[movie] += 1

        if not DEBUG:
            updateRating(user, movie, rating, timestamp);

        #print(f"User {user} rated {movie}: {rating}")
        #print(f"{movie} has been rated {movies[movie]} times")

    if validated:
        global RATINGS_COUNT
        global AVERAGE_RATING

        RATINGS_COUNT += 1
        AVERAGE_RATING += rating

        if RATINGS_COUNT > WINDOW_OF_AVERAGE_RATINGS:
            addAveRating();

    return validated

def updateRating(user, movie, rating, timestamp):
    session = Session()
    try:

        #check to see if user already has a rating for this movie, if yes update with new rating
        listing = session.query(Rating).filter_by(user_id = user, movie_id = movie)

        oldRating = listing.first()

        if oldRating:
            #print("MEEPMEEP")
            #print(f"Updating rating, user: {user}, movie: {movie}, rating: {rating}, time: {timestamp}")
            #print(oldRating)
            listing.update(
              {"rating": rating, "time_stamp": timestamp} ,synchronize_session=False
            )


        #if user has not rated the movie, add a new rating to the Ratings Table
        else:
            newRating = Rating(
               user,
               movie,
               rating,
               timestamp
            )
            session.add(newRating)

        session.commit()

        #Test to make sure the rows are being updated
        #if oldRating:
            #listing = session.query(Rating).filter_by(user_id = user, movie_id = movie)
            #oldRating = listing.first()
            #print(oldRating)
            #print("MEEPMEEP")


        session.close()

    except IntegrityError:
        print("Integrity Error adding: user: {user}, movie: {movie}, rating: {rating}, time: {timestamp}, ROLLBACK")
        session.rollback()

def addAveRating():
    global RATINGS_COUNT
    global AVERAGE_RATING

    session = Session()
    try:
        newRatingAverage = RatingAverage(
           AVERAGE_RATING/RATINGS_COUNT,
           datetime.now()
        )
        print(newRatingAverage)

        if newRatingAverage.averageRating < 3:
            print("Data drift detected! Average rating under 3 stars, consider retraining model")

        session.add(newRatingAverage)
        session.commit()
        session.close()
        RATINGS_COUNT = 0
        AVERAGE_RATING = 0

    except IntegrityError:
        print("Integrity Error adding an Average Rating {newRatingAverage} ROLLBACK")
        session.rollback()

def processMessage(message, last_timestamp, DEBUG = False):
    messageSplits = message.split(',')
    validated = True
    str_timestamp = messageSplits[0]
    timestamp = None

    #checks to see if the timestamp string has seconds and minutes included
    str_timestamp = str_timestamp.split(".")[0]
    temp = str_timestamp.split(":")

    #TIMESTAMP VERIFICATION
    if(len(temp) == 2):
        str_timestamp = str_timestamp + ":00"
    elif(len(temp) == 1):
        str_timestamp = str_timestamp + ":00:00"

    try:
        timestamp = datetime.strptime(str_timestamp, "%Y-%m-%dT%H:%M:%S")

    except:
        print(f"Error {message} has invalid timestamp: {str_timestamp} not in %Y-%m-%dT%H:%M:%S")
        return None

    if timestamp < last_timestamp:
       print(f"Error {timestamp} not after {last_timestamp}")
       return None

    #USER VERIFICATION
    try:
        user = int(messageSplits[1])
    except:
        print(f"Error: {message} User {messageSplits[1]} must be a valid int")
        return None

    if user not in range(0,1000001):
        print(f"Error: user not in valid range of users: {user}")
        return None

    elif len(messageSplits) == 3:
        splits = messageSplits[2].split('/')

        if splits[1] == "rate":
            validated = processRating(splits[2], user, timestamp, DEBUG)


    return timestamp

if __name__ == "__main__":
    Base.metadata.create_all(engine)

    consumer = KafkaConsumer(
        TOPIC_NAME,
        bootstrap_servers=[KAFKA_SERVER],
        auto_offset_reset='latest',
    )

    last_timestamp = datetime.now() - relativedelta(years=500)

    for data in consumer:
        message = data.value.decode()
        #print(message)

        temp_timestamp = processMessage(message, last_timestamp)

        if temp_timestamp:
            last_timestamp = temp_timestamp - relativedelta(seconds=500)
