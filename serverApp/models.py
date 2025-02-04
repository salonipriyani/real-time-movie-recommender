
from serverApp.extensions import db

class User(db.Model):
    user_id = db.Column(db.Integer)
    movie_id = db.Column(db.String)
    rating = db.Column(db.Integer)
    __table_args__ = (
        db.PrimaryKeyConstraint(user_id, movie_id),
        {},
    )

    def to_dict(self):
        return {
            'movie': self.movie_id,
            'user': self.user_id,
            'rating': self.rating
        }
