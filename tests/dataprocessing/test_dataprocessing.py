import sys
sys.path.append("../..")

from dataprocessing.consumeKafka import processRating
from dataprocessing.consumeKafka import processMessage

from datetime import datetime

#processRating assumes timestamp and user have already been validated
def test_process_rating():
    validData = "whisper+of+the+heart+1995=3"
    validUser = 10
    validTimestamp = datetime.now()

    invalidRatingData = ["whisper+of+the+heart+1995=6","whisper+of+the+heart+1995=-1", "whisper+of+the+heart+1995="]
    invalidMovieData = ["whisper+of+the+heart+1700=3","whisper+of+the+heart+2050=3", "whisper+of+the+heart+abra=3"]

    #valid movie, valid rating
    assert  True == processRating(validData, validUser, validTimestamp, True)

    #valid movie, invalid rating
    for case in invalidRatingData:
        #print(case)
        assert False == processRating(case, validUser, validTimestamp, True)

    #invalid movie year, valid rating
    for case in invalidMovieData:
        #print(case)
        assert False == processRating(case, validUser, validTimestamp, True)

def test_process_message():

    validMessages = ["2023-03-23T14:18:27,728418,GET /data/m/high+plains+drifter+1973/14.mpg", "2023-03-23T14:19:49,258066,GET /rate/a+night+out+1915=5"]
    invalidTimestamps = ["2023-03-23dT14:18:27,728418,GET /data/m/high+plains+drifter+1973/14.mpg", "2023-03-23dT14:18:40,728418,GET /data/m/high+plains+drifter+1973/14.mpg", "2023-03-23T,258066,GET /rate/a+night+out+1915=5", "2023-03-23T-2,258066,GET /rate/a+night+out+1915=5"]
    invalidUserIDs = ["2023-03-23T14:18:27,-1,GET /data/m/high+plains+drifter+1973/14.mpg", "2023-03-23T14:18:27,1000001,GET /data/m/high+plains+drifter+1973/14.mpg", "2023-03-23T14:18:27,abc,GET /data/m/high+plains+drifter+1973/14.mpg"]

    validTimestamp = datetime.strptime("2023-03-23T14:18:26", "%Y-%m-%dT%H:%M:%S")

    for case in validMessages:
        #print(case)
        print(processMessage(case, validTimestamp, True))
        assert validTimestamp < processMessage(case, validTimestamp, True)

    #invalid timestamp
    for case in invalidTimestamps:
        #print(case)
        assert None == processMessage(case, validTimestamp, True)

    #invalid user ID
    for case in invalidUserIDs:
        #print(case)
        assert None == processMessage(case, validTimestamp, True)

if __name__ == "__main__":
    test_process_rating()
    test_process_message()
