from db import db

from models.halts import Halts

class Route(db.Model):
    __tablename__ = 'route'

    id = db.Column(db.Integer, primary_key=True)
    source_id = db.Column(db.Integer, db.ForeignKey(Halts.id), nullable=False)
    destination_id = db.Column(db.Integer, db.ForeignKey(Halts.id), nullable=False)

    source = db.relationship('Halts', foreign_keys=[source_id], backref='route_sources', uselist=False)
    destination = db.relationship('Halts', foreign_keys=[destination_id], backref='route_destinations', uselist=False)