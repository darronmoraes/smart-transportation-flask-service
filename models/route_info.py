from db import db

from models.route import Route
from models.halts import Halts

class RouteInfo(db.Model):
    __tablename__ = 'route_info'

    id = db.Column(db.Integer, primary_key=True)
    route_id = db.Column(db.Integer, db.ForeignKey(Route.id), nullable=False)
    source_id = db.Column(db.Integer, db.ForeignKey(Halts.id), nullable=False)
    destination_id = db.Column(db.Integer, db.ForeignKey(Halts.id), nullable=False)
    distance = db.Column(db.String(50), nullable=False)
    fare = db.Column(db.String(50), nullable=False)

    route = db.relationship('Route', backref='route_info', uselist=False)
    source = db.relationship('Halts', foreign_keys=[source_id], backref='route_info_sources', uselist=False)
    destination = db.relationship('Halts', foreign_keys=[destination_id], backref='route_info_destinations', uselist=False)