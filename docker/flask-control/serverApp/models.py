
from serverApp.database import db
from sqlalchemy import Column, String, DateTime, Integer, PrimaryKeyConstraint, Float

class User(db.Model):
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
