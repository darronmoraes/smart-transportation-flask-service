from datetime import time

from db import db

from models.route import Route

class Schedule(db.Model):
    __tablename__ = 'schedule'

    id = db.Column(db.Integer, primary_key=True)
    departure_at = db.Column(db.Time)
    arrival_at = db.Column(db.Time)
    duration = db.Column(db.String(45), nullable=False)
    route_id = db.Column(db.Integer, db.ForeignKey(Route.id), nullable=False)

    route = db.relationship('Route', backref='schedule', uselist=False)