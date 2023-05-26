# from datetime import datetime, time

from db import db
from flask import Flask, jsonify, request, current_app
from flask_mysqldb import MySQL
from flask_marshmallow import Marshmallow
from flask_cors import CORS
# import apschedulers BackgroundScheduler and IntervalTrigger
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger

from resources.user import bp as UserBluprint
from resources.passenger import bp as PassengerBluprint
from resources.employee import bp as EmployeeBluprint
from resources.schedule import bp as ScheduleBluprint
from resources.bus import bp as BusBluprint
from resources.booking import bp as BookingBluprint
from resources.location import bp as LocationBluprint

# import Pass model for scheduling
from models.pass_model import Pass

# import constants
from consts import UPLOAD_FOLDER


app = Flask(__name__)

marshmallow = Marshmallow()
mysql = MySQL(app)

CORS(app)


# connect db
# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:root@localhost/sts_test'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:root1234@sts-dev.cd6q49enrqry.ap-south-1.rds.amazonaws.com/sts_test'
db.init_app(app)

# Secret Key
# app.config['SECRET_KEY'] = 'smarttransportationsystem2023'

# Upload profile image folder path
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Create a scheduler
scheduler = BackgroundScheduler(daemon=True)
scheduler.start()

# Scheduled job to update pass status daily
scheduler.add_job(Pass.update_pass_status, args=[app], trigger=IntervalTrigger(days=1))

# Scheduler to reset usage_counter
scheduler.add_job(Pass.reset_usage_counter, 'cron', hour=1, minute=0, args=[app])

# route blueprint from resources
app.register_blueprint(UserBluprint)
app.register_blueprint(PassengerBluprint)
app.register_blueprint(EmployeeBluprint)
app.register_blueprint(ScheduleBluprint)
app.register_blueprint(BusBluprint)
app.register_blueprint(BookingBluprint)
app.register_blueprint(LocationBluprint)



if __name__ == '__main__':
    # app.run(debug=True)
    # app.run(host='192.168.0.112', debug=True)
    # run on all ip addresses
    app.run(host='0.0.0.0', debug=True)
    # app.run(host='0.0.0.0', port=5000)