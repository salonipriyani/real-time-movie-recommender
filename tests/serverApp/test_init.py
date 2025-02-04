import pytest
import sys
from mock import patch
import pandas as pd 
import random
sys.path.append("../..")
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
from serverApp import create_app


def test_create_app():
    returned_app = create_app()
    assert returned_app is not None

