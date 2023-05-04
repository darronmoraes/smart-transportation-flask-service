from datetime import date

from db import db

from models.halts import Halts
from models.passenger import Passenger
from models.bus_schedules import BusSchedules

class Ticket(db.Model):
    __tablename__ = 'ticket'

    id = db.Column(db.Integer, primary_key=True)
    booked_at = db.Column(db.DateTime, nullable=False)
    total_fare_amount = db.Column(db.Integer, nullable=False)
    distance_travelled = db.Column(db.String(10), nullable=False)
    passenger_count = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(20), nullable=False, default="Booked")
    source_id = db.Column(db.Integer, db.ForeignKey(Halts.id), nullable=False)
    destination_id = db.Column(db.Integer, db.ForeignKey(Halts.id), nullable=False)
    passenger_id = db.Column(db.Integer, db.ForeignKey(Passenger.id), nullable=False)
    bus_schedule_id = db.Column(db.Integer, db.ForeignKey(BusSchedules.id), nullable=False)
    # payment_id = db.Column(db.Integer, db.ForeignKey(RouteInfo.id), nullable=False)

    bus_schedule = db.relationship('BusSchedules', backref='ticket', uselist=False)
    source = db.relationship('Halts', foreign_keys=[source_id], backref='ticket_sources', uselist=False)
    destination = db.relationship('Halts', foreign_keys=[destination_id], backref='ticket_destinations', uselist=False)