from flask import Blueprint, jsonify, request
from db import db

from models.route import Route
from models.source import Source
from models.destination import Destination
from models.route_info import RouteInfo



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
            "destination-id": route.destination_id,
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



@bp.route("/add-destination", methods=["POST"])
def add_destination():
    # get source and destination
    name = request.json.get("name")
    longitude = request.json.get("longitude")
    latitude = request.json.get("latitude")

    if not longitude or not latitude:
        return jsonify({
            'success': False,
            'message': 'longitutde and destination are required to create a destination',
            'status': 400}), 400
    
    if not name:
        return jsonify({
            'success': False,
            'message': 'destination name is required to create a destination',
            'status': 400}), 400
    
    existing_destination = Destination.query.filter_by(name=name).first()
    if existing_destination:
        return jsonify({
            'success': False,
            'message': 'destination already exists',
            'status': 400}), 400
    
    # create new route
    new_destination = Destination(name=name, longitude=longitude, latitude=latitude)
    db.session.add(new_destination)
    db.session.commit()

    # return route added successfully
    return jsonify({
        'success': True,
        'message': 'destination added successfully',
        'status': 200,
        'user-admin': {'destination-id': new_destination.id,
                        'destination-name': new_destination.name,
                        'long': new_destination.longitude,
                        'lat': new_destination.latitude}}), 200