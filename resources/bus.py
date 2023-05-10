from flask import Blueprint, jsonify, request, session
from datetime import datetime
import json

from db import db

from models.bus import Bus
from models.bus_schedules import BusSchedules
from models.route_info import RouteInfo
from models.route import Route
from models.halts import Halts


bp = Blueprint("bus", __name__, url_prefix="/bus")



@bp.route("/bus", methods=["GET", "POST"])
def bus():
    buses = Bus.query.all()
    bus_list = []
    for bus in buses:
        bus_list.append({'id': bus.id, 'rto-reg-no': bus.reg_no, 'capacity': bus.capacity, 'type': bus.type, 'status': bus.status})
    return jsonify({'bus': bus_list})


@bp.route("/add-bus-details", methods=["POST"])
def bus_details():
    reg_no = request.json.get("register-no")
    capacity = request.json.get("capacity")
    type = request.json.get("type")
    status = request.json.get("status")

    # registered number required
    if not reg_no:
        return jsonify({
            'success': False,
            'message': 'registration number is required',
            'status': 400}), 400
    
    # check for exisiting bus details
    existing_bus = Bus.query.filter_by(reg_no=reg_no).first()
    if existing_bus:
        return jsonify({
            'success': False,
            'message': 'bus already registered',
            'status': 400}), 400
    
    # add bus details if not exisiting
    new_bus = Bus(reg_no=reg_no, capacity=capacity, type=type, status=status)
    db.session.add(new_bus)
    db.session.commit()

    # return registration success
    return jsonify({
        'success': True,
        'message': 'bus registered successfully',
        'status': 200}), 200


@bp.route("/add-bus-schedule", methods=["POST"])
def bus_schedule():
    bus_id = request.json.get("bus-id")
    schedule_id = request.json.get("schedule-id")
    # available_seats = request.json.get("available-seats")
    date = request.json.get("date")

    # required check
    if not bus_id and schedule_id and date:
        return jsonify({
            'success': False,
            'message': 'bus and schedule details required and also date',
            'status': 400}), 400
    
    # check for exisiting bus schedule
    existing_schedule = BusSchedules.query.filter_by(bus_id=bus_id, schedule_id=schedule_id, date=date).first()
    if existing_schedule:
        return jsonify({
            'success': False,
            'message': 'bus already scheduled',
            'status': 400}), 400
    
    # get available seats
    bus_details = Bus.query.filter_by(id=bus_id).first()
    available_seats = bus_details.capacity
    
    # add bus details if not exisiting
    new_bus_schedule = BusSchedules(bus_id=bus_id, schedule_id=schedule_id, available_seats=available_seats, date=date)
    db.session.add(new_bus_schedule)
    db.session.commit()

    # return registration success
    return jsonify({
        'success': True,
        'message': 'bus scheduled successfully',
        'status': 200}), 200


@bp.route("/bus-schedule", methods=["GET", "POST"])
def get_bus_schedule():
    bus_schedule = BusSchedules.query.all()
    bus_schedule_list = []
    for bus in bus_schedule:
        bus_schedule_list.append({'bus-id': bus.bus_id, 'schedule-id': bus.schedule_id, 'available-seats': bus.available_seats, 'date': bus.date})
    return jsonify({'bus': bus_schedule_list})




@bp.route("/search", methods=["GET"])
def bus_available_search():
    source_id = request.args.get('source')
    destination_id = request.args.get('destination')
    date_str = request.args.get('date')

    # convert date
    date = datetime.strptime(date_str, '%Y-%m-%d').date()

    # query route-info model to find the route between source and destination
    route_query = db.session.query(Halts, RouteInfo).\
        join(RouteInfo, RouteInfo.source_id == Halts.id).\
        filter(RouteInfo.source_id == source_id, RouteInfo.destination_id == destination_id)

    route_info = route_query.first()

    # query bus-schedule model to find the available date
    bus_schedules = BusSchedules.query.filter(BusSchedules.date == date).all()

    if not bus_schedules:
        return jsonify({
            'success': False,
            'message': 'no buses available on this route for the specific date',
            'status': 400
        }), 400

    available_buses = []

    for bus_schedule in bus_schedules:
        # get the route information from the schedule
        route_stand = bus_schedule.schedule.route
        # get the source and destination stands from the route info
        source_stand = route_stand.source_stand
        destination_stand = route_stand.destination_stand

        # query halts table to get source and destination names
        source_halt = Halts.query.get(source_id)
        destination_halt = Halts.query.get(destination_id)

        available_bus_result = {
            'schedule': {
                'id': bus_schedule.id,
                'departure': bus_schedule.schedule.departure_at.strftime('%H:%M'),
                'arrival': bus_schedule.schedule.arrival_at.strftime('%H:%M'),
                'duration': bus_schedule.schedule.duration,
                'departure-stand': source_stand,
                'arrival-stand': destination_stand,
                'date': bus_schedule.date.strftime('%Y-%m-%d'),
                'seats-available': bus_schedule.available_seats
            },
            'bus': {
                'id': bus_schedule.bus.id,
                'reg-no': bus_schedule.bus.reg_no,
                'type': bus_schedule.bus.type
            },
            'route': {
                'source': source_halt.name,
                'source-id': source_halt.id,
                'destination': destination_halt.name,
                'destination-id': destination_halt.id,
                'distance': route_info.RouteInfo.distance,
                'fare': route_info.RouteInfo.fare
            }
        }
        available_buses.append(available_bus_result)

    return jsonify({
        'success': True,
        'status': 200,
        'results': available_buses
    }), 200




# seat-available route
@bp.route('/seat-available', methods=['POST'])
def check_availability():
    bus_id = request.args.get('bus-id')
    passenger_count = int(request.args.get('passenger-count'))
    date_str = request.args.get('date')

    # convert date
    date = datetime.strptime(date_str, '%Y-%m-%d').date()

    if not bus_id and not passenger_count and not date:
        return jsonify({
            'success': False,
            'message': 'No schedule and passenger count provided.',
            'status': 400}), 400
    
    bus_schedule = BusSchedules.query.filter_by(bus_id=bus_id, date=date).first()

    if not bus_schedule:
        return jsonify({
            'success': False,
            'message': 'No buses available for the specified date',
            'status': 400}), 400
    
    available_seats = bus_schedule.available_seats

    if available_seats < passenger_count:
        return jsonify({
            'success': False,
            'message': 'Not enough seats available for the specified number of passengers',
            'status': 400}), 400
    
    return jsonify({
            'success': True,
            'available-seats': available_seats,
            'status': 200}), 200