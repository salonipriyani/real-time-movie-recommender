import numpy as np
import pytest
import sys
sys.path.append("../../..")

from evaluation.online.online_personalization import PersonalizationMetric


@pytest.fixture
def sample_responses():
    return [
        "2023-03-20T21:05:05.522889,751093,recommendation request 17645-team12.isri.cmu.edu:8082, status 200, result: rear+window+1954, the+shawshank+redemption+1994, louis+c.k.+oh+my+god+2013, shoah+1985, generation+kill+2008, the+empire+strikes+back+1980, the+godfather+1972, prime+suspect+1991, the+usual+suspects+1995, the+civil+war+1990, the+wrong+trousers+1993, star+wars+1977, the+silence+of+the+lambs+1991, a+great+day+in+harlem+1994, for+the+birds+2000, django+unchained+2012, casablanca+1942, tipping+the+velvet+2002, the+lord+of+the+rings+the+two+towers+2002, the+lord+of+the+rings+the+fellowship+of+the+ring+2001, 457 ms",
    ]


def test_extract_movie_recommendations(sample_responses):
    expected_movies = [
        [
            "rear window 1954",
            "the shawshank redemption 1994",
            "louis c.k. oh my god 2013",
            "shoah 1985",
            "generation kill 2008",
            "the empire strikes back 1980",
            "the godfather 1972",
            "prime suspect 1991",
            "the usual suspects 1995",
            "the civil war 1990",
            "the wrong trousers 1993",
            "star wars 1977",
            "the silence of the lambs 1991",
            "a great day in harlem 1994",
            "for the birds 2000",
            "django unchained 2012",
            "casablanca 1942",
            "tipping the velvet 2002",
            "the lord of the rings the two towers 2002",
            "the lord of the rings the fellowship of the ring 2001",
        ],
    ]


    result = PersonalizationMetric.extract_movie_recommendations(sample_responses)
    assert result == expected_movies


def test_create_binary_matrix(sample_responses):

    movie_lists = PersonalizationMetric.extract_movie_recommendations(sample_responses)
    binary_matrix = PersonalizationMetric.create_binary_matrix(movie_lists)

    assert binary_matrix.shape == (1, 20)
    assert binary_matrix.sum() == 20
    assert binary_matrix[0].tolist().count(1) == 20


def test_calculate_personalization(sample_responses):

    personalization_metric = PersonalizationMetric()
    for response in sample_responses:
        personalization_metric.add_response(response)

    personalization_score = personalization_metric.calculate_personalization()
    assert isinstance(personalization_score, float)
    assert 0 <= personalization_score <= 1

def test_calculate_personalization_last_n(sample_responses):
    personalization_metric = PersonalizationMetric()
    for response in sample_responses:
        personalization_metric.add_response(response)

    personalization_score_last_1 = personalization_metric.calculate_personalization_last_n(1)
    personalization_score_last_10 = personalization_metric.calculate_personalization_last_n(10)

    assert isinstance(personalization_score_last_1, float)
    assert 0 <= personalization_score_last_1 <= 1
    assert isinstance(personalization_score_last_10, float)
    assert 0 <= personalization_score_last_10 <= 1
