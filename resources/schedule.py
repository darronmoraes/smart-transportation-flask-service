from flask import Blueprint, jsonify, request
from db import db

from datetime import datetime

from models.route import Route
from models.halts import Halts
from models.route_info import RouteInfo
from models.schedule import Schedule
from models.bus_schedules import BusSchedules
from models.route_type import RouteType


bp = Blueprint("route", __name__, url_prefix="/schedule")



@bp.route("/route-info", methods=["GET"])
def get_routes_info():
    # query to join route_info on route to get all details of routes-info
    routesInfo = RouteInfo.query.join(Route, RouteInfo.route_id == Route.id).all()
    routes_info_list = []
    for routeInfo in routesInfo:

        # query route-info source and destination
        source = routeInfo.source.name
        destination = routeInfo.destination.name

        route_info_data = {
            "id": routeInfo.route_id,
            "source": {
                "id": routeInfo.source_id,
                "name": source
            },
            "destination": {
                "id": routeInfo.destination_id,
                "name": destination
            },
            "distance": routeInfo.distance,
            "fare": routeInfo.fare
        }

        # query if route-info has route-type data and add to route-info-data
        route_type = db.session.query(RouteType).filter_by(route_info_id=routeInfo.id).first()
        if route_type and route_type.type:
            route_info_data["type"] = route_type.type

        # append route-info-list with route-info-data
        routes_info_list.append(route_info_data)
    return jsonify({
        'result': routes_info_list,
        'status': 200,
        'success': True
        }), 200


@bp.route("/add-route", methods=["POST"])
def add_route():
    # get source and destination
    source = request.json.get("source")
    destination = request.json.get("destination")

    if not source or not destination:
        return jsonify({
            'success': False,
            'message': 'source and destination are required to create a route',
            'status': 400}), 400
    
    existing_route = Route.query.filter_by(source_stand=source, destination_stand=destination).first()
    if existing_route:
        return jsonify({
            'success': False,
            'message': 'route already exists',
            'status': 405}), 400
    
    # create new route
    new_route = Route(source_stand=source, destination_stand=destination)
    db.session.add(new_route)
    db.session.commit()

    # return route added successfully
    return jsonify({
        'success': True,
        'message': 'route added successfully',
        'status': 200,
        'result': {'route-id': new_route.id,
                        'source': new_route.source_stand,
                        'destination': new_route.destination_stand}}), 200



@bp.route("/route", methods=["GET"])
def get_routes():
    # query to join route_info and route to get all details of driver
    routes = Route.query.all()
    routes_list = []
    for route in routes:
        routes_list.append({
            "route-id": route.id,
            "source": route.source_stand,
            "destination": route.destination_stand
        })
    return jsonify({
        'success': True,
        'status': 200,
        'result': routes_list }), 200



@bp.route("/add-halt", methods=["POST"])
def add_halt():
    # get source and destination
    name = request.json.get("name")
    longitude = request.json.get("longitude")
    latitude = request.json.get("latitude")

    if not longitude or not latitude:
        return jsonify({
            'success': False,
            'message': 'longitutde and destination are required to create a source',
            'status': 400}), 400
    
    if not name:
        return jsonify({
            'success': False,
            'message': 'source name is required to create a source',
            'status': 400}), 400
    
    existing_source = Halts.query.filter_by(name=name).first()
    if existing_source:
        return jsonify({
            'success': False,
            'message': 'source already exists',
            'status': 400}), 400
    
    # create new route
    new_source = Halts(name=name, longitude=longitude, latitude=latitude)
    db.session.add(new_source)
    db.session.commit()

    # return route added successfully
    return jsonify({
        'success': True,
        'message': 'source added successfully',
        'status': 200,
        'result': {'source-id': new_source.id,
                        'source-name': new_source.name,
                        'long': new_source.longitude,
                        'lat': new_source.latitude}}), 200



@bp.route("/add-route-info", methods=["POST"])
def create_dynamic_routes():
    # get source and destination
    route_id = request.json.get("route-id")
    source_id = request.json.get("source-id")
    destination_id = request.json.get("destination-id")
    distance = request.json.get("distance")
    fare = request.json.get("fare")
    route_type = request.json.get("route-type")


    # required route source name
    if not route_id:
        return jsonify({
            'success': False,
            'message': 'route-id name not provided',
            'status': 400}), 400
    
    # required source name
    if not source_id:
        return jsonify({
            'success': False,
            'message': 'source-id is required to create a routeinfo',
            'status': 400}), 400
    
    if not destination_id:
        return jsonify({
            'success': False,
            'message': 'destination-id is required to create a routeinfo',
            'status': 400}), 400
    
    # check if route with source name exists
    existing_route_info = db.session.query(Halts)\
        .join(RouteInfo, Halts.id == RouteInfo.source_id)\
        .filter(Halts.id == source_id).first()
    if existing_route_info:
        return jsonify({
            'success': False,
            'message': 'route info already exists',
            'status': 400}), 400
    
    existing_route_type = db.session.query(RouteType)\
        .filter_by(route_info_id=route_id).first()
    if existing_route_info and existing_route_type and route_type == 'SHUTTLE':
        return jsonify({
            'success': False,
            'message': 'route info already exists having route type',
            'status': 400}), 400
    
    if route_id and source_id and destination_id:
        # create new route
        new_route_info = RouteInfo(route_id=route_id, source_id=source_id, destination_id=destination_id, distance=distance, fare=fare)
        db.session.add(new_route_info)
        db.session.commit()

        # if user provides route-type than populate the route-type model
        if route_type:
            # create new route type
            new_route_type = RouteType(type=route_type, route_info_id=new_route_info.id)
            db.session.add(new_route_type)
            db.session.commit()

    # return route added successfully
    return jsonify({
        'success': True,
        'message': 'route info added successfully',
        'status': 200,
        'result': {'route-id': new_route_info.route_id,
                    'source-name': new_route_info.source_id,
                    'destination-name': new_route_info.destination_id,
                    'distance': new_route_info.distance,
                    'fare': new_route_info.fare}}), 200



@bp.route("/add-schedule", methods=["POST"])
def create_schedule():
    # get departure and  arrival time and duration with route-id 
    departure_at_str = request.json.get("departure-at")
    arrival_at_str = request.json.get("arrival-at")
    duration = request.json.get("duration")
    route_id = request.json.get("route-id")

    # convert string to time type
    departure_at = datetime.strptime(departure_at_str, '%H:%M').time()
    arrival_at = datetime.strptime(arrival_at_str, '%H:%M').time()

    # required route source name
    if not departure_at and not arrival_at:
        return jsonify({
            'success': False,
            'message': 'departure and arrival time are required',
            'status': 400}), 400
    
    # check if route with source name exists
    exisiting_schedule = Schedule.query.filter(Schedule.departure_at==departure_at, Schedule.route_id==route_id).first()
    if exisiting_schedule:
        return jsonify({
            'success': False,
            'message': 'schedule already exists',
            'status': 400}), 400
    
    
    # create a new schedule if it doesn't exist
    new_schedule = Schedule(departure_at=departure_at, arrival_at=arrival_at, duration=duration, route_id=route_id)
    db.session.add(new_schedule)
    db.session.commit()

    departure = new_schedule.departure_at.strftime('%H:%M')
    arrival = new_schedule.arrival_at.strftime('%H:%M')

    # return route added successfully
    return jsonify({
        'success': True,
        'message': 'schedule info added successfully',
        'status': 200,
        'schedule': {'schedule-id': new_schedule.id,
                     'departure-time': departure,
                     'arrival-time': arrival,
                     'duration': new_schedule.duration,}}), 200


@bp.route("/schedules", methods=["GET"])
def get_schedules():
    # query to join route_info and route to get all details of driver
    schedules = Schedule.query.join(Route, Schedule.route_id == Route.id).all()

    schedules_list = []
    for schedule in schedules:
        # convert date
        departure = schedule.departure_at.strftime('%H:%M')
        arrival = schedule.arrival_at.strftime('%H:%M')
        schedules_list.append({
            "id": schedule.id,
            "departure-at": departure,
            "arrival-at": arrival,
            "duration": schedule.duration,
            "route-source": schedule.route.source_stand,
            "route-destination": schedule.route.destination_stand,
        })
    return jsonify({
            'success': True,
            'result': schedules_list,
            'status': 200}), 200


        
# get all bus schedules for a given date
@bp.route('/search', methods=['GET'])
def bus_schedule_available():
    date_str = request.args.get('date')

    # convert date
    date = datetime.strptime(date_str, '%Y-%m-%d').date()

    # query bus-schedule model to find the available schedules on the given date
    bus_schedules = BusSchedules.query.filter(BusSchedules.date == date).all()

    if not bus_schedules:
        return jsonify({
            'success': False,
            'message': 'No buses available on the specified date',
            'status': 400
        }), 400
    
    available_buses = []

    for bus_schedule in bus_schedules:
        # Check if the schedule is on the specified date  
        if bus_schedule.date == date:
            # Get the schedule object
            schedule = Schedule.query.get(bus_schedule.schedule_id)

            # Query to filter departure and arrival stands by filter schedule model
            route = Route.query.filter_by(id=schedule.route_id).first()

            available_bus_result = {
                'schedule-info': {
                    'id': bus_schedule.id,
                    'date': bus_schedule.date.strftime('%Y-%m-%d'),
                    'seats-available': bus_schedule.available_seats,
                    'schedule': {
                        'id': schedule.id,
                        'departure': schedule.departure_at.strftime('%H:%M'),
                        'arrival': schedule.arrival_at.strftime('%H:%M'),
                        'duration': schedule.duration,
                        'departure-stand': route.source_stand,
                        'arrival-stand': route.destination_stand
                    }
                },
                'bus': {
                    'id': bus_schedule.bus.id,
                    'reg-no': bus_schedule.bus.reg_no,
                    'type': bus_schedule.bus.type
                }
            }
            available_buses.append(available_bus_result)

    return jsonify({
        'success': True,
        'status': 200,
        'results': available_buses
    }), 200

