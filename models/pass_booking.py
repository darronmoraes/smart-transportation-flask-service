from datetime import datetime, time

from db import db

from models.pass_model import Pass
from models.bus_schedules import BusSchedules

class PassBooking(db.Model):
    __tablename__ = 'pass_booking'

    id = db.Column(db.Integer, primary_key=True)
    booked_at = db.Column(db.DateTime, nullable=False)
    pass_id = db.Column(db.Integer, db.ForeignKey(Pass.id), nullable=False)
    bus_schedule_id = db.Column(db.Integer, db.ForeignKey(BusSchedules.id), nullable=False)

    pass_model = db.relationship('Pass', backref='pass_booking', uselist=False)
    bus_schedule = db.relationship('BusSchedules', backref='pass_booking', uselist=False)


    # method to allocate bus having schedule (bus_schedule model)
    @staticmethod
    def allocate_pass_to_bus_schedule(pass_id, bus_schedule_id, booked_at):
        # query to get bus-schedule if exists
        bus_schedule = BusSchedules.query.get(bus_schedule_id)

        if bus_schedule.available_seats > 0:
            # Retrieve pass
            pass_model = Pass.query.get(pass_id)
            if pass_model:
                 # Create a new PassBooking entry
                new_booking = PassBooking(
                    booked_at=booked_at,
                    pass_id=pass_id,
                    bus_schedule_id=bus_schedule_id
                )

                # Update available seats in bus-schedule model
                bus_schedule.available_seats -= 1
                # add new PassBooking entry
                db.session.add(new_booking)
                db.session.commit()

                # Allocation successful
                return True
        else:
            # Seats not available
            db.session.rollback()
            return False