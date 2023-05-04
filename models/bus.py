from db import db

class Bus(db.Model):
    __tablename__ = 'bus'

    id = db.Column(db.Integer, primary_key=True)
    reg_no = db.Column(db.String(45))
    capacity = db.Column(db.Integer)
    type = db.Column(db.String(45), nullable=False)
    status = db.Column(db.String(45))