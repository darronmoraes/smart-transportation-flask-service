from flask import Blueprint, jsonify, request, session, current_app
import json
from datetime import datetime
# for file upload securely
from werkzeug.utils import secure_filename
# upload files
import os
import uuid


from models.user import User
from models.passenger import Passenger


from db import db

from middleware.auth import auth_middleware

from utils.pic_utils import allowed_file

bp = Blueprint("passenger", __name__, url_prefix="/user")



@bp.route("/passenger", methods=["GET", "POST"])
def get_passengers():
    passengers = Passenger.query.all()
    passenger_list = []
    for passenger in passengers:
        passenger_list.append({'id': passenger.id, 'user': {'firstname': passenger.firstname, 'lastname': passenger.lastname, 'userId': passenger.user_id, 'photo': passenger.photo}})
    return jsonify(passenger_list)



@bp.route("/add-passenger-details", methods=["POST"])
@auth_middleware
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
        'message': 'passenger details added successfully',
        'status': 200,
        'passenger': {
            'id': passenger.id,
            'first-name': passenger.firstname,
            'last-name': passenger.lastname,
            'contact': passenger.contact,
            'address': passenger.address,
            'category': passenger.category,
            'gender': passenger.gender,
            'dob': passenger.dob}}), 200



# upload profile image function having app level permissions
def home(app, passenger_id):
    # passenger_id = request.json.get('passenger-id')

    # check if passenger id is provided
    if not passenger_id:
        return jsonify({
            'status': 401, 
            'message': 'passenger-id not provided', 
            'success': False}), 401

    # Check if passenger exists in db
    existing_passenger = Passenger.query.get(passenger_id)
    if not existing_passenger:
        return jsonify({
            'status': 402, 
            'message': 'passenger-id does not exists', 
            'success': False}), 402

    if 'photo' not in request.files:
        return jsonify({
            'status': 403, 
            'message': 'no file', 
            'success': False}), 403

    photo = request.files['photo']

    # photo selected check
    if photo.filename == '':
        return jsonify({
            'status': 406, 
            'message': 'no file selected', 
            'success': False}), 406

    # photo extension check
    if not allowed_file(photo.filename):
        return jsonify({
            'status': 407, 
            'message': 'photo file type not allowed', 
            'success': False}), 407


    # save photo
    if photo and allowed_file(photo.filename):
        # generate unique filename
        unique_filename = str(uuid.uuid4()) + '-' + datetime.now().strftime('%Y%m%d%H%M%S') + secure_filename(photo.filename)
        # save the file to disk
        photo.save(os.path.join(app.config['UPLOAD_FOLDER'], unique_filename))

        # update passenger's profile image in db
        existing_passenger.photo = unique_filename
        db.session.commit()

        # Construct the photo URL or data based on your requirements
        photo_url = f"https://127.0.0.1:5000/file/pic/{unique_filename}"

        return jsonify({
            'status': 200, 
            'message': 'Photo uploaded successfully',
            'photo_url': photo_url,  # Include the photo URL or data in the response
            'success': True
        }), 200

    return jsonify({
        'status': 400, 
        'message': 'Invalid file format', 
        'success': False}), 400


@bp.route('/upload-pic/<int:passenger_id>', methods=['POST'])
@auth_middleware
def upload_pic(passenger_id):
    return home(current_app, passenger_id)