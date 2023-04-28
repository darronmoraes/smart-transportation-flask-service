from flask import Blueprint, jsonify, request
from db import db

import datetime

from models.route import Route
from models.source import Source
from models.route_info import RouteInfo
from models.schedule import Schedule



bp = Blueprint("route", __name__, url_prefix="/schedule")



@bp.route("/route", methods=["GET"])
def get_routes():
    # query to join route_info and route to get all details of driver
    routes = RouteInfo.query.join(Route, RouteInfo.route_id == Route.id).all()
    routes_list = []
    for route in routes:
        routes_list.append({
            "route-id": route.route_id,
            "source-id": route.source_id,
            "destination": route.destination,
            "distance": route.distance,
            "fare": route.fare
        })
    return jsonify(routes_list)


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
        'user-admin': {'route-id': new_route.id,
                        'source': new_route.source_stand,
                        'destination': new_route.destination_stand}}), 200



@bp.route("/add-source", methods=["POST"])
def add_source():
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
    
    existing_source = Source.query.filter_by(name=name).first()
    if existing_source:
        return jsonify({
            'success': False,
            'message': 'source already exists',
            'status': 400}), 400
    
    # create new route
    new_source = Source(name=name, longitude=longitude, latitude=latitude)
    db.session.add(new_source)
    db.session.commit()

    # return route added successfully
    return jsonify({
        'success': True,
        'message': 'source added successfully',
        'status': 200,
        'user-admin': {'source-id': new_source.id,
                        'source-name': new_source.name,
                        'long': new_source.longitude,
                        'lat': new_source.latitude}}), 200



@bp.route("/add-route-info", methods=["POST"])
def create_dynamic_routes():
    # get source and destination
    route_source = request.json.get("stand-name")
    source_name = request.json.get("source-name")
    destination_name = request.json.get("destination-name")
    distance = request.json.get("distance")
    fare = request.json.get("fare")


    # required route source name
    if not route_source:
        return jsonify({
            'success': False,
            'message': 'route source name not provided',
            'status': 400}), 400
    
    # required source name
    if not source_name:
        return jsonify({
            'success': False,
            'message': 'source name is required to create a routeinfo',
            'status': 400}), 400
    
    # check if route with source name exists
    exisiting_route_info = db.session.query(Source)\
        .join(RouteInfo, Source.id == RouteInfo.source_id)\
        .filter(Source.name == source_name).first()
    if exisiting_route_info:
        return jsonify({
            'success': False,
            'message': 'route info already exists',
            'status': 400}), 400
    
    # to get the route id
    route = Route.query.filter_by(source_stand=route_source).first()
    # to get the source id
    source = Source.query.filter_by(name=source_name).first()
    if route and source:
        # route_info = RouteInfo.query.filter_by(route_id=route.id).first()
        # create new route
        new_route_info = RouteInfo(route_id=route.id, source_id=source.id, destination=destination_name, distance=distance, fare=fare)
        db.session.add(new_route_info)
        db.session.commit()

    # return route added successfully
    return jsonify({
        'success': True,
        'message': 'route info added successfully',
        'status': 200,
        'route info': {'route-id': new_route_info.route.id,
                        'source-name': new_route_info.source.id,
                        'destination-name': new_route_info.destination,
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
    departure_at = datetime.datetime.strptime(departure_at_str, '%H:%M').time()
    arrival_at = datetime.datetime.strptime(arrival_at_str, '%H:%M').time()

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