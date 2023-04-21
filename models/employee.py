from datetime import datetime
from db import db

from models.user import User
from models.driver import Driver

class Employee(db.Model):
    __tablename__ = 'employee'

    id = db.Column(db.Integer, primary_key=True)
    firstname = db.Column(db.String(45), nullable=False)
    lastname = db.Column(db.String(45), nullable=False)
    contact = db.Column(db.String(10), nullable=False, unique=True, info={'check_constraint': 'length(contact) = 10'})
    gender = db.Column(db.String(6), nullable=False)
    role = db.Column(db.String(10), nullable=False)
    employee_no = db.Column(db.String(10), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey(User.id), nullable=False)
    driver_id = db.Column(db.Integer, db.ForeignKey(Driver.id), nullable=False)
    # user = db.relationship('User', backref="employee", uselist=False)
    driver = db.relationship('Driver', backref='employee', uselist=False)