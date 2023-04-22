from db import db


class Driver(db.Model):
    __tablename__ = 'driver'

    id = db.Column(db.Integer, primary_key=True)
    license_no = db.Column(db.String(45), nullable=False)