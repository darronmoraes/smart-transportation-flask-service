from flask import Blueprint, jsonify, request
from datetime import datetime

# Database configuration
from db import db

# Models
from models.bus import Bus
from models.bus_schedules import BusSchedules
from models.ticket import Ticket
from models.halts import Halts

# Blueprint configuration
bp = Blueprint("report", __name__,  url_prefix="/report")


# Report based on bus and date
@bp.route('/bus-report', methods=['GET'])
def get_bus_report():
    bus_id = request.args.get('bus-id')
    date = request.args.get('date')

    if not bus_id or not date:
        return jsonify({
            'message': 'Invalid request. Please provide bus-id and date',
            'status': 401,
            'success': False
        }), 401
    
    # Query the bus information
    bus = Bus.query.get(bus_id)

    if not bus:
        return jsonify({
            'message': 'Bus not found',
            'status': 402,
            'success': False
        }), 402
    
    # Query the schedules for the bus on the given date
    bus_schedules = BusSchedules.query.filter_by(bus_id=bus_id).filter(BusSchedules.date == date).all()

    if not bus_schedules:
        return jsonify({
            'message': 'No schedules found for the bus on given date',
            'status': 403,
            'success': False
        }), 403
    
    report = {
        'bus': {
            'id': bus.id,
            'reg-no': bus.reg_no,
            'type': bus.type
        },
        'date': date,
        'schedules': []
    }

    for bus_schedule in bus_schedules:
        # Query the associated schedule for each bus schedule
        schedule =  bus_schedule.schedule

        # Query the route for each schedule
        route = schedule.route

        # source and destination
        source_id = route.source_id
        destination_id = route.destination_id

        # Retrieve names of source and destination halts
        source_halt = Halts.query.get(source_id)
        destination_halt = Halts.query.get(destination_id)

        # Query the tickets for each bus schedule
        tickets = Ticket.query.filter_by(bus_schedule_id=bus_schedule.id).all()

        schedule_data = {
            'id': schedule.id,
            'departure': schedule.departure_at.strftime('%Y-%m-%d'),
            'arrival': schedule.departure_at.strftime('%Y-%m-%d'),
            'route': {
                'id': route.id,
                'source': {
                    'id': source_id,
                    'name': source_halt.name
                },
                'destination': {
                    'id': source_id,
                    'name': source_halt.name
                }
            },
            'tickets': [{
                'id': ticket.id,
                'fare-amount': ticket.total_fare_amount,
                'distance': ticket.distance_travelled,
                'passenger_count': ticket.passenger_count,
                'status': ticket.status,
            } for ticket in tickets]
        }

        report['schedules'].append(schedule_data)

    return jsonify({
        'success': True,
        'result': report,
        'status': 200
    }), 200