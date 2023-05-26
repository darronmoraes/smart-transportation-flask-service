from flask import Blueprint, jsonify, request, session
from db import db

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