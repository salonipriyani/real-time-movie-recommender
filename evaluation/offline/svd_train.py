import numpy as np
import pandas as pd
from datetime import datetime
import os

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Column, String, DateTime, Integer, PrimaryKeyConstraint, Float

from surprise import Dataset
from surprise import Reader
from surprise import SVD
from surprise.model_selection import GridSearchCV
from surprise.accuracy import rmse
from surprise import dump

import mlflow
import mlflow.sklearn

def readFromFile(file_path):
    df = pd.read_csv(file_path)[["user_id","movie","rating"]]
    return df

def dataSplit(dataframe, name, now):
    train = dataframe.sample(frac=0.8, random_state=645)
    train.to_csv(f'{name}_train.csv', index=True, index_label="Unnamed: 0")

    test = dataframe.drop(train.index)
    test.to_csv(f'{name}_test.csv', index=True, index_label="Unnamed: 0")
    return train, test

def parameterTune(train):
    param_grid = {
        "n_epochs": [5, 10, 50],
        "lr_all": [0.002, 0.005],
        "reg_all": [0.1, 0.4, 0.6]
    }
    gs = GridSearchCV(SVD, param_grid, measures=["rmse"], cv=2) #5
    gs.fit(train)

    # Best hyperparameters and corresponding RMSE and MAE
    print(f"Best hyperparameters: {gs.best_params['rmse']}")
    print(f"Best RMSE: {gs.best_score['rmse']}")

    return gs.best_params["rmse"]

def trainModel(best_params, train):
    # Extract and train model with best params
    svd_algo = SVD(n_epochs=best_params['n_epochs'],
                   lr_all=best_params['lr_all'],
                   reg_all=best_params['reg_all'])
    
    # Build trainset object
    trainingSet = train.build_full_trainset()
    svd_algo.fit(trainingSet)
    return svd_algo

def evalModel(svd_algo, test, name):
    # Predict ratings for the test set
    test_data = test.construct_testset(test.raw_ratings)
    test_predictions = svd_algo.test(test_data)

    # Calculate RMSE and MAE for the test set
    rmse_test = rmse(test_predictions, verbose=False)
    print(f"Model {name} Test RMSE: {rmse_test}")
    
    return test_predictions, rmse_test


def readFromDB(now):
    engine = create_engine('postgresql://root:password@localhost:5432/sqlalchemy')
    connection = engine.connect()
    df = pd.read_sql('ratings', connection)
    connection.close()
    engine.dispose()

    df = df.rename(columns={'movie_id':'movie'})
    
    df = df.iloc[-50000:]
        
    df.to_csv(f'evaluation/offline/trainingLogs/ratings_train_data_{now}.csv',index=True, index_label="Unnamed: 0")
    mlflow.log_artifact(f'evaluation/offline/trainingLogs/ratings_train_data_{now}.csv')
    df.to_csv(f'/home/team12/team12/group-project-s23-the-everything-model/docker/flask-control/modeling/baseline_train.csv',index=True, index_label="Unnamed: 0")
    
    return df


def readFromDBSplit(now):
    engine = create_engine('postgresql://root:password@localhost:5432/sqlalchemy')
    connection = engine.connect()
    df = pd.read_sql('ratings', connection)
    users = pd.read_sql('users_table', connection)
    connection.close()
    engine.dispose()
    
    df = df.rename(columns={'movie_id':'movie'})
    
    males = users[users["gender"] == 'M'].iloc[-50000:]
    females = users[users["gender"] == 'F'].iloc[-50000:]

    males = df.merge(males, on="user_id").drop(columns=["age", "occupation"])
    females = df.merge(females, on="user_id").drop(columns=["age", "occupation"])
    
    males.to_csv(f'evaluation/offline/trainingLogs/males_ratings_train_data_{now}.csv',index=True, index_label="Unnamed: 0")
    mlflow.log_artifact(f'evaluation/offline/trainingLogs/males_ratings_train_data_{now}.csv')
    females.to_csv(f'evaluation/offline/trainingLogs/females_ratings_train_data_{now}.csv',index=True, index_label="Unnamed: 0")
    mlflow.log_artifact(f'evaluation/offline/trainingLogs/females_ratings_train_data_{now}.csv')
    
    males.to_csv(f'/home/team12/team12/group-project-s23-the-everything-model/docker/flask-experiment/modeling/male_train.csv',index=True, index_label="Unnamed: 0")
    females.to_csv(f'/home/team12/team12/group-project-s23-the-everything-model/docker/flask-experiment/modeling/female_train.csv',index=True, index_label="Unnamed: 0")
    
    return males, females



def train_pipline(df, name, now):
    # Split into train and test set
    train, test = dataSplit(df,name,now)

    # Load data
    train_df = Dataset.load_from_df(train[["user_id", "movie", "rating"]], Reader(rating_scale=(1, 5)))
    test_df = Dataset.load_from_df(test[["user_id", "movie", "rating"]], Reader(rating_scale=(1, 5)))
    
    # hyperparameter tuning using gridsearchcv with 5-fold cross validation simultaneously.
    """
    lr_all is the learning rate for all parameters (how much the parameters are adjusted in each iteration)
    reg_all is the regularization term for all parameters, which is a penalty term added to prevent overfitting.
    """
    best_params = parameterTune(train_df)
    
    # Train SVD model using the best_params
    svd_algo = trainModel(best_params, train_df)

    # Evaluate the final SVD model using test_df
    test_predictions, rmse_test = evalModel(svd_algo, test_df, name)
    
    # Save the model
    dump.dump(f'evaluation/offline/models/SVD_{name}_{now}.dump', algo=svd_algo)
    if name == "baseline":
        dump.dump(f'/home/team12/team12/group-project-s23-the-everything-model/docker/flask-control/modeling/SVD_{name}.dump', algo=svd_algo)
    else:
        #/home/team12/team12/group-project-s23-the-everything-model/docker/flask-experiment/modeling
        dump.dump(f'/home/team12/team12/group-project-s23-the-everything-model/docker/flask-experiment/modeling/SVD_{name}.dump', algo=svd_algo)

    mlflow.log_artifact(f'evaluation/offline/models/SVD_{name}_{now}.dump')


if __name__ == '__main__':
    experiment_name = "my-experiment"
    # Get the experiment object by name
    experiment = mlflow.get_experiment_by_name(experiment_name)
    
    if experiment is None:
        print("Experiment '{}' not found. Creating a new experiment...".format(experiment_name))
        experiment_id = mlflow.create_experiment(experiment_name)
        experiment = mlflow.get_experiment_by_name(experiment_name)
    
    with mlflow.start_run(run_name="my-run", experiment_id=experiment.experiment_id):
        # Create an MLflow client
        client = mlflow.tracking.MlflowClient()
        experiment_id = mlflow.get_experiment_by_name(experiment_name).experiment_id
        latest_run = client.search_runs(experiment_ids=[experiment_id], order_by=["start_time desc"], max_results=1)
        dir_path = latest_run[0].info.artifact_uri
        print(latest_run[0].info.artifact_uri)
        print(latest_run[0].info.run_id)
    
        now = datetime.now()

        #file = "evaluation/offline/ratings.csv"

        df = readFromDB(now)
        print("df")

        # Split into train and test set
        #train, test = dataSplit(df)
        df_males, df_females = readFromDBSplit(now)
        print("datasplit")

        ######### train baseline model ###########
        train_pipline(df,"baseline",now)
        print("baseline")

        ######### train baseline model ###########
        train_pipline(df_females,"female",now)
        print("female")

        ######### train baseline model ###########
        train_pipline(df_males,"male",now)
        print("male")
        
        mlflow.end_run()
        
    # Set the environment variable
    file_names = os.listdir(dir_path[7:])
    file_paths = [f for f in file_names]
    file_paths.sort()
    print(file_paths)
    
    """
    flask-control
    ENV MODEL=$model
    ENV DATA=$data
    
    flask-experiment
    ENV FEMALE_MODEL=$female_model
    ENV FEMALE_DATA=$female_data
    ENV MALE_MODEL=$male_model
    ENV MALE_DATA=$male_data

    """
    os.environ['MODEL'] = file_paths[0]
    os.environ['DATA'] = file_paths[5]
    
    os.environ['FEMALE_MODEL'] = file_paths[1]
    os.environ['FEMALE_DATA'] = file_paths[3]
    os.environ['MALE_MODEL'] = file_paths[2]
    os.environ['MALE_DATA'] = file_paths[4]

    # Path to the .env file on the host machine
    env_file_path = "/home/team12/team12/group-project-s23-the-everything-model/docker/.env"

    # Write the modified contents back to the file
    with open(env_file_path, "w") as f:
        f.write('FEMALE_MODEL='+file_paths[1]+"\n")
        f.write('FEMALE_DATA='+file_paths[3]+"\n")
        f.write('MALE_MODEL='+file_paths[2]+"\n")
        f.write('MALE_DATA='+file_paths[4]+"\n")
        f.write('MODEL='+file_paths[0]+"\n")
        f.write('DATA='+file_paths[5]+"\n")
          
