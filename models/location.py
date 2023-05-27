from datetime import datetime, time

from db import db

# models
from models.employee import Employee


class Location(db.Model):
    __tablename__ = 'location'

    id = db.Column(db.Integer, primary_key=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    lat = db.Column(db.Float, nullable=False)
    lng = db.Column(db.Float, nullable=False)
    employee_id = db.Column(db.Integer, db.ForeignKey(Employee.id), nullable=False)