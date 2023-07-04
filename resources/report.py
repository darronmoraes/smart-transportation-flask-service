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
    
    # Report response
    report = {
        'bus': {
            'id': bus.id,
            'reg-no': bus.reg_no,
            'type': bus.type
        },
        'date': date,
        'schedules': []
    }
    
    # For storing ticket information
    total_fare_amount = 0
    total_tickets = 0
    passenger_count = 0

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

        # Iterate over tickets for calculations
        for ticket in tickets:
            total_fare_amount += ticket.total_fare_amount
            total_tickets += 1
            passenger_count += ticket.passenger_count

        # Dictionary for the schedule
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
            'ticket': {
                'total-fare-amount': total_fare_amount,
                'total-tickets': total_tickets,
                'passenger-count': passenger_count
            }
        }

        # Append schedules data to the report
        report['schedules'].append(schedule_data)

        # Reset the calculation variables for the next schedule
        total_fare_amount = 0
        total_tickets = 0
        passenger_count = 0

    return jsonify({
        'success': True,
        'result': report,
        'status': 200
    }), 200