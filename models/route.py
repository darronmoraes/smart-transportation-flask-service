from db import db

class Route(db.Model):
    __tablename__ = 'route'

    id = db.Column(db.Integer, primary_key=True)
    source_stand = db.Column(db.String(45), nullable=False)
    destination_stand = db.Column(db.String(45), nullable=False)