import pytest
import sys
sys.path.append("../../..")
import random
import pandas as pd
import numpy as np
from surprise import Dataset
from surprise import Reader
from surprise import SVD
from surprise.model_selection import GridSearchCV
from surprise.accuracy import rmse
from surprise import dump

from evaluation.offline.svd_train import (
    readFromFile,
    dataSplit,
    parameterTune,
    trainModel,
    evalModel,
)


@pytest.fixture
def sample_csv():
    random.seed(645)
    data = {'user_id': [random.randint(1000,100000) for i in range(20)],
            'movie': ["rear+window+1954", "the+shawshank+redemption+1994", 
                      "louis+c.k.+oh+my+god+2013", "shoah+1985", 
                      "generation+kill+2008", "the+empire+strikes+back+1980", 
                      "the+godfather+1972", "prime+suspect+1991", 
                      "the+usual+suspects+1995", "the+civil+war+1990", 
                      "the+wrong+trousers+1993", "star+wars+1977", 
                      "the+silence+of+the+lambs+1991", "a+great+day+in+harlem+1994", 
                      "for+the+birds+2000", "django+unchained+2012", 
                      "casablanca+1942", "tipping+the+velvet+2002", 
                      "the+lord+of+the+rings+the+two+towers+2002", "the+lord+of+the+rings+the+fellowship+of+the+ring+2001"],
            'rating': [random.randint(1,5) for i in range(20)]}
    df = pd.DataFrame(data)
    return df

def test_readFromFile(sample_csv):
    #df = readFromFile("ratings.csv")
    df = sample_csv
    assert (df.columns == ["user_id","movie","rating"]).all()
    assert df.rating.dtype == 'int64'
    assert (df.rating >= 1).all() and (df.rating <= 5).all() 
    
def test_dataSplit(sample_csv):
    train, test = dataSplit(sample_csv)
    row, col = sample_csv.shape
    train_row, train_col = train.shape
    test_row, test_col = test.shape
    
    assert test_row + train_row == row
    assert train_col == col
    assert test_col == col
    assert int(row * 0.8) == train_row 
    assert int(row * 0.2) == test_row 
    
def test_parameterTune(sample_csv):
    train, test = dataSplit(sample_csv)
    train_df = Dataset.load_from_df(train[["user_id", "movie", "rating"]], Reader(rating_scale=(1, 5)))
    best_param = parameterTune(train_df)
    
    assert len(best_param.keys()) == 3 #{'n_epochs': 5, 'lr_all': 0.002, 'reg_all': 0.1}
      
def test_evalModel(sample_csv):
    train, test = dataSplit(sample_csv)
    train_df = Dataset.load_from_df(train[["user_id", "movie", "rating"]], Reader(rating_scale=(1, 5)))
    test_df = Dataset.load_from_df(test[["user_id", "movie", "rating"]], Reader(rating_scale=(1, 5)))
    best_param = parameterTune(train_df)
    svd_algo = trainModel(best_param, train_df)
    test_predictions, rmse_test = evalModel(svd_algo,test_df)
    preds = []
    for i in test_predictions:
        pred = i.r_ui
        preds.append(pred)
        
    assert len(test_predictions) == len(test)
    assert rmse_test > 0
    assert all(isinstance(x, float) for x in preds)
    assert all(x >= 0 and x <= 5 for x in preds)
    


