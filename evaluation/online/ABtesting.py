import os
import sys
from os import path

import numpy as np
from datetime import datetime
from kafka import KafkaConsumer
from sklearn.metrics.pairwise import cosine_similarity
from tqdm import tqdm
from collections import deque

from scipy.spatial.distance import cosine
from scipy.stats import ttest_ind
# from online_personalization import *
import random
import pandas as pd

from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from base import Session, engine, Base
from sqlalchemy import Column, String, DateTime, Integer, PrimaryKeyConstraint, Float

maxlen = 1000

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

def log_personalization_metric(control,test, start_time, log_dir="log"):
    log_file_name = f"{start_time.strftime('%Y-%m-%d_%H-%M-%S')}.log"
    log_path = os.path.join(log_dir, log_file_name)

    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    personalization_control = control.calculate_personalization()
    personalization_test = test.calculate_personalization()

    with open(log_path, "a") as log_file:
        log_file.write(f"{datetime.now()}\tControl personalization: {personalization_control:.4f}\tTest Personalization: {personalization_test:.4f}\n")

# class Recommendation(Base):
#      __tablename__ = 'recommendations'

#      user_id = Column(Integer)
#      model_id = Column(String)
#      data_id = Column(String) 
#      recommendation = Column(String)
#      time_stamp = Column(DateTime)
   

#      __table_args__ = (
#          PrimaryKeyConstraint(user_id, time_stamp),
#          {},
#      )

#      def __init__(self, user, model, data, recommendation, time_stamp):
#         self.user_id = user
#         self.model_id = movie
#         self.data_id = data
#         self.recommendation = recommendation
#         self.time_stamp = time_stamp


#      def __repr__(self) -> str:
#          #return f"Recommendation(user_id={self.user_id!r}, movies={self.movie1_id!r}, {self.movie2_id!r}, {self.movie3_id!r}, {self.movie4_id!r}, {self.movie5_id!r}, {self.movie6_id!r}, {self.movie7_id!r}, {self.movie8_id!r}, {self.movie9_id!r}, {self.movie10_id!r}, timestamp={self.time_stamp!r})"
#          return f"Recommendation(user_id={self.user_id!r}, model= {self.model_id}, data= {self.data_id}, Recommendation= {self.recommendation}, timestamp={self.time_stamp!r})"

class Recommendation_With_Pipeline(Base):
     __tablename__ = 'recommendations_with_pipeline'

     user_id = Column(Integer)
     model_id = Column(String)
     data_id = Column(String) 
     pipeline_id = Column(String)
     recommendation = Column(String)
     time_stamp = Column(DateTime)
   

     __table_args__ = (
         PrimaryKeyConstraint(user_id, time_stamp),
         {},
     )

     def __init__(self, user, model, data, pipeline, recommendation, time_stamp):
        self.user_id = user
        self.model_id = movie
        self.data_id = data
        self.pipeline_id = pipeline
        self.recommendation = recommendation
        self.time_stamp = time_stamp


     def __repr__(self) -> str:
         #return f"Recommendation(user_id={self.user_id!r}, movies={self.movie1_id!r}, {self.movie2_id!r}, {self.movie3_id!r}, {self.movie4_id!r}, {self.movie5_id!r}, {self.movie6_id!r}, {self.movie7_id!r}, {self.movie8_id!r}, {self.movie9_id!r}, {self.movie10_id!r}, timestamp={self.time_stamp!r})"
         return f"Recommendation(user_id={self.user_id!r}, model= {self.model_id}, data= {self.data_id}, pipeline= {self.pipeline_id}, Recommendation= {self.recommendation}, timestamp={self.time_stamp!r})"

# def datafromDB(uid, rec):
#     Base = declarative_base()
#     engine = create_engine('postgresql://root:password@localhost:5432/sqlalchemy')
#     session = Session()

#     listing = session.query(Recommendation.model_id).filter_by(user_id = uid, recommendation=rec).order_by(Recommendation.time_stamp.desc())
#     return listing.first()

def capture_response(control_metric,test_metric, control_score, test_score, pool_size=maxlen):
    cap = pool_size
    count = 0
    c_count = 0
    t_count = 0
    total_processed = 0
    start_time = datetime.now()
    control_per = 0.0
    test_per = 0.0
    res = ""
    statement = ""
    t_stat = 0.0
    p_value = 0.0
    test_mean, control_mean =0.0,0.0
    try:
        for message in consumer:
            message = message.value.decode()
            splits = message.split(",")

            if splits[2] == "recommendation request 17645-team12.isri.cmu.edu:8082":

                result = splits[4:24]
                result[0] = result[0].replace(" result: ", "")
                result = [s.strip().replace(' ', '') for s in result]
                session = Session()
                rec = ",".join(result)

                user = int(splits[1])

                listing = session.query(Recommendation_With_Pipeline.model_id).filter_by(user_id = user, recommendation=rec).order_by(Recommendation_With_Pipeline.time_stamp.desc())
                # print(listing.first()[0])
                if listing.first()==None:
                    continue
                
                result = listing.first()[0]
                # print(result)
                # print(message)

               
                iscontrol = "baseline" in result
                session.close()
                if iscontrol:
                    control_metric.add_response(message)
                    c_count +=1
                else:
                    test_metric.add_response(message)
                    t_count +=1

                count +=1
                total_processed += 1

                if t_count + c_count >= cap:
                    count -= 1

                if total_processed % 1000 == 0:
                    log_personalization_metric(control_metric,test_metric, start_time)

                current_time = datetime.now()
                elapsed_time = current_time - start_time
                
                if iscontrol:
                    control_per = control_metric.calculate_personalization_last_n(50)
                    control_score.add_score(control_per)
                else:
                    test_per = test_metric.calculate_personalization_last_n(50)
                    test_score.add_score(test_per)
                
                a, b, c, d,e,f= ABtest(control_score,test_score)
                if a != None:
                    res = a
                if b != None:
                    statement = b
                if c != None:
                    t_stat=c
                if d != None:
                    p_value=d 
                if e != None:
                    control_mean=d 
                if f != None:
                    test_mean=f  
                
                sys.stdout.write(
                    f"\033[2K\rStart Time: {start_time}, Current Time: {current_time}, "
                    f"Top {c_count+t_count}/{total_processed} processed! control vs Test {c_count}:{t_count}\n\033[2K\r"
                    f"Control Group Personalization (last 50): {control_per:.4f}\n\033[2K\r"
                    f"Test Group Personalization (last 50): {test_per:.4f}\n\033[2K\r"
                    f"Control mean: {control_mean}\n\033[2K\r"
                    f"Test mean: {test_mean}\n\033[2K\r"
                    f"Result: {res}\n{statement}\n\033[2K\r"
                    f"t_stat: {t_stat:.3f}\n\033[2K\r"
                    f"P value: {p_value:.8f}\033[F\033[F\033[F\033[F\033[F\033[F\033[F\033[F"
                )
                sys.stdout.flush()

                  
    except KeyboardInterrupt:
        print("\nExiting script")
        return personalization_control.responses


class rollingscore:
    def __init__(self):
        self.scores = deque(maxlen=100)
    
    def add_score(self,score):
        self.scores.append(score)
    def __len__(self):
        return len(self.scores)
    def total(self):
        return sum(self.scores)

    
def ABtest(control, test):
    result, statement=None,None 
    t_stat, p_value = None, None
    test_mean, control_mean = None, None
    if len(control) == len(test):
        # Calculate means and standard deviations for both groups
        control_mean = sum(control.scores) / len(control)
        control_std = pd.Series(control.scores).std()
        test_mean = sum(test.scores) / len(test)
        test_std = pd.Series(test.scores).std()

        # Calculate t-test statistic and p-value
        t_stat, p_value = ttest_ind(control.scores, test.scores)

        if p_value < 0.05:
            result = "Null hypothesis win!"
            statement = "The difference in personalization scores between the control and test groups is significant."
        else:
            result = "Alternative hypothesis win!"
            statement = "The difference in personalization scores between the control and test groups is NOT significant."
        
        # print(control_mean, test_mean)
    return result, statement, t_stat, p_value, control_mean, test_mean



if __name__ == "__main__":
    # create kafka consumer
    topic = "movielog12"
    consumer = KafkaConsumer(
        topic,
        bootstrap_servers=["localhost:9092"],
        auto_offset_reset="latest",
    )

    control_group_metric = PersonalizationMetric(maxlen=1000)
    test_group_metric = PersonalizationMetric(maxlen=1000)
    
    control_scores = rollingscore()
    test_scores = rollingscore()
    
    # if iscontrol:
    #     responses = capture_response(control_group_metric,"control")
    # else:
    #     responses = capture_response(test_group_metric,"test")

    responses = capture_response(control_group_metric,test_group_metric, control_scores, test_scores)
    print("end")


