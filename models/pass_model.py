from datetime import datetime, time

from db import db

from models.halts import Halts
from models.passenger import Passenger
from models.route_info import RouteInfo

class Pass(db.Model):
    __tablename__ = 'pass'

    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    valid_from = db.Column(db.Date, nullable=False)
    valid_to = db.Column(db.Date, nullable=False)
    usage_counter = db.Column(db.Integer, nullable=False, default=0)
    status = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)
    route_info_id = db.Column(db.Integer, db.ForeignKey(RouteInfo.id), nullable=False)
    passenger_id = db.Column(db.Integer, db.ForeignKey(Passenger.id), nullable=False)
    # payment_id = db.Column(db.Integer, db.ForeignKey(Passenger.id), nullable=False)

    route_info = db.relationship('RouteInfo', backref='pass', uselist=False)



    # static method to update status field to expire after valid_to
    @staticmethod
    def update_pass_status(app):
        with app.app_context():
            # get current date
            current_date = datetime.now().date()
            # filter out passes that are valid_to < current date and status == active
            expired_passes = Pass.query.filter(Pass.valid_to < current_date, Pass.status == 'active').all()

            # loop through expired and mark status as expired
            for p in expired_passes:
                p.status = 'expired'

            # commit the changes
            db.session.commit()

    
    # static method to update usage-counter field for each day instanc
    @staticmethod
    def reset_usage_counter(app):
        with app.app_context():
            # get current time
            current_time = datetime.now().time()

            # Check if its 01:00 hours
            if current_time.hour == 1 and current_time.minute == 0:
                # Reset usage_counter to 0 for all passes
                passes = Pass.query.filter(Pass.usage_counter >= 1).all()

                # loop through all passes and set usage_counter to 0
                for p in passes:
                    p.usage_counter = 0
                
                # Commit changes
                db.session.commit()