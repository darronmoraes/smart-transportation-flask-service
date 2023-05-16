from datetime import date

from db import db

from models.bus import Bus
from models.schedule import Schedule
from models.employee import Employee

class BusSchedules(db.Model):
    __tablename__ = 'bus_schedules'

    id = db.Column(db.Integer, primary_key=True)
    bus_id = db.Column(db.Integer, db.ForeignKey(Bus.id), nullable=False)
    schedule_id = db.Column(db.Integer, db.ForeignKey(Schedule.id), nullable=False)
    employee_id = db.Column(db.Integer, db.ForeignKey(Employee.id), nullable=False)
    available_seats = db.Column(db.Integer, nullable=False)
    date = db.Column(db.Date, nullable=False)

    bus = db.relationship('Bus', backref='bus_schedules', uselist=False)
    schedule = db.relationship('Schedule', backref='bus_schedules', uselist=False)
    employee = db.relationship('Employee', backref='bus_schedules', uselist=False)