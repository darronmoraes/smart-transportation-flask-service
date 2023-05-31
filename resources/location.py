from flask import Blueprint, jsonify, request, session
from db import db

from datetime import datetime

from models.location import Location
from models.bus_schedules import BusSchedules


bp = Blueprint("location", __name__, url_prefix="/location")


@bp.route('/', methods=['GET'])
def location():
    locations = Location.query.all()
    location_list = []
    for location in locations:
        location_list.append({
            'id': location.id,
            'updated-at': location.updated_at,
            'longitude': location.lng,
            'latitude': location.lat,
        })

    return jsonify({
        'success': True,
        'status': 200,
        'result': location_list}), 200


@bp.route('/bus-schedule/<schedule_id>/update-location', methods=['PUT'])
def update_location(schedule_id):
    # Retrieve the BusSchedule based on the schedule_id
    bus_schedule = BusSchedules.query.get(schedule_id)

    # Check if the driver's role is 'driver'
    if bus_schedule.employee.role == 'driver':
        # Retrieve the updated latitude and longitude from the driver
        latitude = request.json.get('latitude')
        longitude = request.json.get('longitude')

        # Create a new Location entry or update the existing one
        if bus_schedule.location:
            location = bus_schedule.location
            location.lat = latitude
            location.lng = longitude
        else:
            location = Location(
                employee_id=bus_schedule.employee_id,
                lat=latitude,
                lng=longitude)
            db.session.add(location)
            # Flush the session to generate the location.id
            db.session.flush()
            # update the Location id in the bus-schedule model
            bus_schedule.location_id = location.id

        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Location updated successfully.',
            'status': 200
        }), 200
    
    else:
        return jsonify({
            'success': False,
            'message': 'Driver not found for the bus schedule.',
            'status': 400
        }), 400
    

# API route to get live bus schedule locations
@bp.route('/locations', methods=['GET'])
def get_live_bus_locations():
    # Retrieve the current date
    current_date = datetime.now().date()

    # Query bus schedules for the current date
    bus_schedules = BusSchedules.query.filter(BusSchedules.date == current_date).all()

    live_locations = []

    for bus_schedule in bus_schedules:
        # Check if the bus has a location associated with it
        if bus_schedule.location:
            location = bus_schedule.location
            latitude = location.lat
            longitude = location.lng

            live_location = {
                'bus_schedule_id': bus_schedule.id,
                'latitude': latitude,
                'longitude': longitude
            }

            live_locations.append(live_location)

    if not live_locations:
        return jsonify({
        'success': False,
        'status': 400,
        'message': 'No buses on schedule for the current date'
    }), 400

    return jsonify({
        'success': True,
        'status': 200,
        'live_locations': live_locations
    }), 200



# Bus Schedule location specific to Bus-schedule-id
@bp.route('/locations/bus-schedule/<int:bus_schedule_id>', methods=['GET'])
def live_bus_schedule_location(bus_schedule_id):

    # Check if the bus schedule id exists in the model
    bus_schedule = BusSchedules.query.get(bus_schedule_id)
    if not bus_schedule:
        return jsonify({
            'success': False,
            'message': f'Bus schedule with ID {bus_schedule_id} does not exist',
            'status': 404
        }), 404

    # Retrieve the current date
    current_date = datetime.now().date()
    # current_date = '2023-05-30'

    # Check if the bus schedule is for the current date 
    # use .date.strftime() to compare with current date
    if bus_schedule.date.strftime('%Y-%m-%d') != current_date:
        return jsonify({
            'success': False,
            'message': f'Bus schedule with ID {bus_schedule_id} is not for the current date',
            'status': 400
        }), 400
    
    # Query the bus schedule's location
    location = Location.query.get(bus_schedule.location_id)
    if not location:
        return jsonify({
            'success': False,
            'message': 'Location data not found',
            'status': 404
        }), 404
    
    # Construct response
    response = {
        'success': True,
        'status': 200,
        'location': {
            'id': location.id,
            'lat': location.lat,
            'lng': location.lng,
            'updated_at': location.updated_at
        }
    }

    return jsonify(response), 200