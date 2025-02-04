from sqlalchemy import Column, String, DateTime, Integer, PrimaryKeyConstraint, Float

from  base import Base

class Rating(Base):
    __tablename__ = 'ratings'

    user_id = Column(Integer)
    movie_id = Column(String)
    rating = Column(Integer)
    time_stamp = Column(DateTime)

    __table_args__ = (
        PrimaryKeyConstraint(user_id, movie_id),
        {},
    )

    def __init__(self, user, movie, rating, time_stamp):
        self.user_id = user
        self.movie_id = movie
        self.rating = rating
        self.time_stamp = time_stamp

    def __repr__(self) -> str:
        return f"Rating(user_id={self.user_id!r}, movie={self.movie_id!r}, rating={self.rating!r}, timestamp={self.time_stamp!r})"

    def to_dict(self):
        return {
            'movie': self.movie_id,
            'user': self.user_id,
            'rating': self.rating,
        }

class RatingAverage(Base):
    __tablename__ = 'average_ratings'

    averageRating = Column(Float)
    update_time = Column(DateTime)

    __table_args__ = (
        PrimaryKeyConstraint(update_time),
        {},
    )

    def __init__(self, averageRating, update_time):
        self.averageRating = averageRating
        self.update_time = update_time

    def __repr__(self) -> str:
        return f"RatingAverage(Average rating of: {self.averageRating!r} at {self.update_time})"

class Recommendation(Base):
     __tablename__ = 'recommendations'

     user_id = Column(Integer)
     model_id = Column(String)
     data_id = Column(String) 
     recommendation = Column(String)
     time_stamp = Column(DateTime)
   

     __table_args__ = (
         PrimaryKeyConstraint(user_id, time_stamp),
         {},
     )

     def __init__(self, user, model, data, recommendation, time_stamp):
        self.user_id = user
        self.model_id = movie
        self.data_id = data
        self.recommendation = recommendation
        self.time_stamp = time_stamp


     def __repr__(self) -> str:
         #return f"Recommendation(user_id={self.user_id!r}, movies={self.movie1_id!r}, {self.movie2_id!r}, {self.movie3_id!r}, {self.movie4_id!r}, {self.movie5_id!r}, {self.movie6_id!r}, {self.movie7_id!r}, {self.movie8_id!r}, {self.movie9_id!r}, {self.movie10_id!r}, timestamp={self.time_stamp!r})"
         return f"Recommendation(user_id={self.user_id!r}, model= {self.model_id}, data= {self.data_id}, Recommendation= {self.recommendation}, timestamp={self.time_stamp!r})"

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


class User(Base):
    __tablename__ = 'users_table'

    user_id = Column(String)
    age = Column(String)
    occupation = Column(String)
    gender = Column(String)
    

    __table_args__ = (
        PrimaryKeyConstraint(user_id),
        {},
    )

    def __init__(self, user, age, occupation, gender):
        self.user_id = user
        self.age = age
        self.occupation = occupation
        self.gender = gender

    def __repr__(self) -> str:
        return f"User(user_id={self.user_id!r}, age={self.age!r}, occupation={self.occupation!r}, gender={self.gender!r})"

    def to_dict(self):
        return {
            'user': self.user_id,
            'age': self.age,
            'occupation': self.occupation,
            'gender': self.gender
        }
