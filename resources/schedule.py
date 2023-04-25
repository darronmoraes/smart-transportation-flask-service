from flask import Blueprint, jsonify, request

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