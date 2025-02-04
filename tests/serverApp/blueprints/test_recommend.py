import pytest
import sys
import random
from mock import patch
import pandas as pd 

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
        'rating': [random.randint(1,5) for i in range(20)],
        'user_id':[random.randint(1000,10000) for i in range(20)],
        'Unnamed: 0.1': [random.randint(1,5) for i in range(20)]}
df = pd.DataFrame(data)
df.to_csv('modeling/ratings_clean.csv')
from serverApp.blueprints.recommend import recommend

 

def test_recommend_not_none():
    movie_list = recommend("1000")
    assert movie_list is not None

def test_recommend_20_movies():
    movie_list = recommend("1111")
    movie_list = movie_list.split(",")
    assert len(movie_list) == 20

def test_recommend_different_movies_to_different_users():
    movie_list1 = recommend("1111")
    movie_list2 = recommend("1234")
    
    assert movie_list1 != movie_list2

def test_recommend_invalid_input():
    movie_list = recommend("test")
    
    assert movie_list == "Please enter a valid user id"