from db import db

from models.route import Route
from models.source import Source

class RouteInfo(db.Model):
    __tablename__ = 'route_info'

    id = db.Column(db.Integer, primary_key=True)
    route_id = db.Column(db.Integer, db.ForeignKey(Route.id), nullable=False)
    source_id = db.Column(db.Integer, db.ForeignKey(Source.id), nullable=False)
    destination = db.Column(db.Integer, nullable=False)
    distance = db.Column(db.String(50), nullable=False)
    fare = db.Column(db.String(50), nullable=False)

    route = db.relationship('Route', backref='route_info', uselist=False)
    source = db.relationship('Source', backref='route_info', uselist=False)