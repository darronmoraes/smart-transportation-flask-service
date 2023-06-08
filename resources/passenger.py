from flask import Blueprint, jsonify, request, session, current_app, send_from_directory, make_response, send_file
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

# import constants
from consts import UPLOAD_FOLDER



bp = Blueprint("passenger", __name__, url_prefix="/user")


# Route to get passenger data **only for testing**
@bp.route("/passenger", methods=['GET'])
def get_passengers():
    passengers = Passenger.query.all()
    
    passenger_list = []
    for passenger in passengers:
        # Filter passenger user data
        user = User.query.get(passenger.user_id)

        passenger_data = {
            'passenger': {
                'id': passenger.id,
                'first-name': passenger.firstname,
                'last-name': passenger.lastname,
                'contact': passenger.contact,
                'address': passenger.address,
                'category': passenger.category,
                'gender': passenger.gender,
                'dob': passenger.dob,
                'photo': passenger.photo
            },
            'user': {
                'id': user.id,
                'email': user.email
            }
        }
        passenger_list.append(passenger_data)

    return jsonify({
        'passengers': passenger_list,
        'status': 200,
        'success': True
    }), 200


# Route to add  Passenger data request
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


# Route to Update passenger data
@bp.route("/passenger-details/<int:passenger_id>", methods=["PUT"])
# @auth_middleware
def update_passenger_details(passenger_id):
    # Check if passenger exists
    passenger = Passenger.query.get(passenger_id)
    if not passenger:
        return jsonify({
            'success': False,
            'message': 'Passenger not found',
            'status': 400
        }), 400
    
    # Update passenger details
    firstname = request.json.get("firstname")
    lastname = request.json.get("lastname")
    contact = request.json.get("contact")
    address = request.json.get("address")
    gender = request.json.get("gender")
    dob = request.json.get("dob")

    # Update firstname if provided
    if firstname:
        passenger.firstname = firstname

    # Update lastname if provided
    if lastname:
        passenger.lastname = lastname

    # Update contact if provided
    if contact:
        passenger.contact = contact

    # Update address if provided
    if address:
        passenger.address = address

    # Update gender if provided
    if gender:
        passenger.gender = gender

    # Update dob if provided
    if dob:
        passenger.dob = dob

    db.session.commit()

    return jsonify({
        'success': True,
        'message': 'Passenger details updated successfully',
        'status': 200,
        'passenger': {
            'id': passenger.id,
            'firstname': passenger.firstname,
            'lastname': passenger.lastname,
            'contact': passenger.contact,
            'address': passenger.address,
            'gender': passenger.gender,
            'dob': passenger.dob
        }
    }), 200


# Route to upload passenger photo
@bp.route('/upload-pic/<int:passenger_id>', methods=['POST'])
@auth_middleware
def upload_pic(passenger_id):
    return home(current_app, passenger_id)

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
        # photo.save(os.path.join(app.config['UPLOAD_FOLDER'], unique_filename))
        photo.save(os.path.join(app.root_path, app.config['UPLOAD_FOLDER'], unique_filename))

        # update passenger's profile image in db
        existing_passenger.photo = unique_filename
        db.session.commit()

        # Construct the photo URL or data based on your requirements
        photo_url = f"http://3.110.42.226/user/file/pic/{unique_filename}"

        return jsonify({
            'status': 200, 
            'message': 'Photo uploaded successfully',
            'photo-url': photo_url,  # Include the photo URL or data in the response
            'file-name': unique_filename,
            'success': True
        }), 200

    return jsonify({
        'status': 400, 
        'message': 'Invalid file format', 
        'success': False}), 400


# Route to get the photo of passenger on filename
@bp.route('/file/pic/<filename>', methods=['GET'])
def get_profile_image_filename(filename):
    return get_filename_image(current_app, filename)

def get_filename_image(app, filename):
    # Retrieve the passenger from the database based on the passenger_id
    passenger = Passenger.query.filter_by(photo=filename).first()

    if not passenger:
        # Handle the case when the passenger or image does not exist
        return jsonify({
            'status': 404,
            'message': 'Image not found',
            'success': False
        }), 404

    # Assuming the uploaded images are stored in the UPLOAD_FOLDER
    image_path = os.path.join(app.root_path, app.config['UPLOAD_FOLDER'], passenger.photo)

    # Return the image file as a response
    return send_file(image_path, mimetype='image/jpeg')



# Route to get the photo of passenger on passenger id
@bp.route('/file/pic/<passenger_id>', methods=['GET'])
@auth_middleware
def get_profile_image(passenger_id):
    return send_passenger_photo(current_app, passenger_id)

def send_passenger_photo(app, passenger_id):
    # Retrieve the passenger from the database based on the passenger_id
    passenger = Passenger.query.get(passenger_id)

    if not passenger or not passenger.photo:
        # Handle the case when the passenger or image does not exist
        return jsonify({
            'status': 404,
            'message': 'Image not found',
            'success': False
        }), 404

    # Assuming the uploaded images are stored in the UPLOAD_FOLDER
    image_path = os.path.join(app.root_path, app.config['UPLOAD_FOLDER'], passenger.photo)

    # Create a response with the image file
    response = make_response(send_file(image_path))

    # Set the Content-Type header to specify the image mimetype
    response.headers['Content-Type'] = 'image/jpeg'

    # Return the image file as a response
    return response