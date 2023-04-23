from datetime import datetime
from db import db

from models.user import User

class Passenger(db.Model):
    __tablename__ = 'passenger'

    id = db.Column(db.Integer, primary_key=True)
    firstname = db.Column(db.String(45), nullable=False)
    lastname = db.Column(db.String(45), nullable=False)
    contact = db.Column(db.String(10), nullable=False, unique=True, info={'check_constraint': 'length(contact) = 10'})
    address = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(45), nullable=False)
    gender = db.Column(db.String(6), nullable=False)
    dob = db.Column(db.DateTime, nullable=False)
    photo = db.Column(db.String(150))
    user_id = db.Column(db.Integer, db.ForeignKey(User.id), nullable=False)