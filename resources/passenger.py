from flask import Blueprint, jsonify, request, session
import json
from models.user import User
from models.passenger import Passenger
from db import db


bp = Blueprint("passenger", __name__, url_prefix="/user")



@bp.route("/passenger", methods=["GET", "POST"])
def get_passengers():
    passengers = Passenger.query.all()
    passenger_list = []
    for passenger in passengers:
        passenger_list.append({'id': passenger.id, 'user': {'firstname': passenger.firstname, 'lastname': passenger.lastname, 'userId': passenger.user_id, 'photo': passenger.photo}})
    return jsonify(passenger_list)



@bp.route("/add-passenger-details", methods=["POST"])
def add_details():
    firstname = request.json.get("firstname")
    lastname = request.json.get("lastname")
    contact = request.json.get("contact")
    address = request.json.get("address")
    category = request.json.get("category")
    gender = request.json.get("gender")
    dob = request.json.get("dob")
    photo = request.json.get("photo")
    user_id = request.json.get("userid")

    # check if email and password are not empty
    if not firstname or not lastname or not contact:
        return jsonify({
            'success': False,
            'message': 'firstname, lastname and contact are required',
            'status': 400}), 400
    
    # create passenger
    passenger = Passenger(firstname=firstname, lastname=lastname, contact=contact, address=address, category=category, gender=gender, dob=dob, photo=photo, user_id=user_id)
    db.session.add(passenger)
    db.session.commit()

    # return added-details success
    return jsonify({
        'success': True,
        'message': 'passenger details registered successfully',
        'status': 200,
        'firstname': passenger.firstname,
        'lastname': passenger.lastname }), 200