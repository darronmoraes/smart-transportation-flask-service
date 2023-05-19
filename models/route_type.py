from db import db

from models.route_info import RouteInfo

class RouteType(db.Model):
    __tablename__ = 'route_type'

    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(10), nullable=False)
    route_info_id = db.Column(db.Integer, db.ForeignKey(RouteInfo.id), nullable=False)

    route_info = db.relationship('RouteInfo', backref='route_type', uselist=False)