from db import db

class Source(db.Model):
    __tablename__ = 'source'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(45), nullable=False)
    longitutde = db.Column(db.String(50), nullable=False)
    latitude = db.Column(db.String(50), nullable=False)