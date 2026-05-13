from db import db

class Predictions(db.Model):
    __tablename__="predictions"

    id= db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    text= db.Column(db.Text, nullable=False)
    result = db.Column(db.String(20), nullable=False)
    confidence= db.Column(db.Float)
    Time= db.Column(db.DateTime, server_default=db.func.now())
