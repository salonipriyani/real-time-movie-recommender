import numpy as np
import pandas as pd
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Column, String, DateTime, Integer, PrimaryKeyConstraint, Float
from scipy.stats import ttest_ind
from surprise import Dataset
from surprise import Reader
from surprise import SVD
from surprise.model_selection import GridSearchCV
from surprise.accuracy import rmse
from surprise import dump
from collections import deque
import mlflow
import mlflow.sklearn
from sklearn.metrics.pairwise import cosine_similarity


maxlen = 1000
class PersonalizationMetric:
    def __init__(self, maxlen=maxlen):
        self.responses = deque(maxlen=maxlen)

    def add_response(self, response):
        self.responses.append(response)

    def calculate_personalization(self):
        movie_lists = self.extract_movie_recommendations(self.responses)
        binary_matrix = self.create_binary_matrix(movie_lists)
        # print(binary_matrix)
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
                for movie in response.split(",")[:-1]
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

def ABtest(control, test):
    result, statement=None,None 
    t_stat, p_value = None, None
    test_mean, control_mean = None, None

    # Calculate means and standard deviations for both groups
    control_mean = sum(control) / len(control)
    control_std = pd.Series(control).std()
    test_mean = sum(test) / len(test)
    test_std = pd.Series(test).std()

    # Calculate t-test statistic and p-value
    t_stat, p_value = ttest_ind(control, test)

    if p_value < 0.05:
        result = "Alternative hypothesis win!"
        statement = "The difference in personalization scores between the Male and Female groups is significant."
    else:
        result = "Null hypothesis win!"
        statement = "The difference in personalization scores between the Male and Female  groups is NOT significant."
    
        # print(control_mean, test_mean)
    return result, statement, t_stat, p_value, control_mean, test_mean

if __name__ == '__main__':

    engine = create_engine('postgresql://root:password@localhost:5432/sqlalchemy')
    connection = engine.connect()
    df = pd.read_sql('recommendations', connection)
    df = df.replace('', np.nan)
    df = df.dropna(subset=['model_id', 'data_id'])
    data = df.sample(n=50000)

    control_df = data[data['model_id'] == 'meep']
    male_df = data[data['model_id'] == 'SVD_male']
    female_df = data[data['model_id'] == 'SVD_female']
    print("The number of data portion: female / male: ", female_df.shape[0]/male_df.shape[0])

    base = control_df['recommendation'].tolist()
    male = male_df['recommendation'].tolist()
    female = female_df['recommendation'].tolist()

    male_metric = PersonalizationMetric(maxlen=1000)
    female_metric = PersonalizationMetric(maxlen=1000)
    
    female_score = []
    male_score = []

    f_count = 0
    for message in female:
        # print(message)
        female_metric.add_response(message)
        f_count +=1
        if f_count> 50:
            f_count = 0
            female_per = female_metric.calculate_personalization_last_n(50)
            female_score.append(female_per)
    m_count = 0
    for message in female:
        male_metric.add_response(message)
        m_count +=1
        if m_count> 50:
            m_count = 0
        male_per = male_metric.calculate_personalization_last_n(50)
        male_score.append(male_per)




    result, statement, t_stat, p_value, control_mean, test_mean= ABtest(female_score,male_score)

    print("t_state: ", t_stat)
    print("p_value: ", p_value)
    print(result)
    print(statement)

