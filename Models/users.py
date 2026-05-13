from db import db

class Users(db.Model):
    __tablename__="users"

    id=db.Column(db.Integer, primary_key=True)
    name=db.Column(db.String(20), nullable=False)
    email=db.Column(db.String(100), nullable=False, unique=True)
    password=db.Column(db.String(255), nullable=False)
    profile_pic=db.Column(db.String(255))

    token_version = db.Column(db.Integer, default=0)

    predictions = db.relationship(
    "Predictions",
    backref="user",
    cascade="all, delete-orphan"
)