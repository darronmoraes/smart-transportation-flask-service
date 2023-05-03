from datetime import date

from db import db

from models.bus import Bus
from models.schedule import Schedule

from models.route import Route

class BusSchedules(db.Model):
    __tablename__ = 'bus_schedules'

    id = db.Column(db.Integer, primary_key=True)
    bus_id = db.Column(db.Integer, db.ForeignKey(Bus.id), nullable=False)
    schedule_id = db.Column(db.Integer, db.ForeignKey(Schedule.id), nullable=False)
    available_seats = db.Column(db.Integer, nullable=False)
    date = db.Column(db.Date, nullable=False)