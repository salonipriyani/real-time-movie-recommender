from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Column, String, DateTime, Integer, PrimaryKeyConstraint, Float

import pandas as pd


engine = create_engine('postgresql://root:password@localhost:5432/sqlalchemy')
Session = sessionmaker(bind=engine)

Base = declarative_base()
Base.metadata.create_all(engine)

users = pd.read_csv("all_users.csv")
users.to_sql(name='users_table', con=engine, if_exists='replace', index=False)

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
        return f"User(user_id={self.user_id!r}, age={self.age!r}, occupation={self.occupation!r}, ge>

    def to_dict(self):
        return {
            'user': self.user_id,
            'age': self.age,
            'occupation': self.occupation,
            'gender': self.gender
        }

session = Session()
listing = session.query(User).filter_by(user_id = "1")
print(listing.first().gender)

