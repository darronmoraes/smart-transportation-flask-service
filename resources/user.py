from flask import Blueprint, jsonify, request, session
import json
from models.user import User
from models.session import Session
from db import db

from utils.email_utils import send_otp_email
from utils.otp_utils import generate_otp, verify_otp


bp = Blueprint("user", __name__, url_prefix="/user")

@bp.route("/user", methods=["GET", "POST"])
def user():
    users = User.query.all()
    user_list = []
    for user in users:
        user_list.append({'id': user.id, 'email': user.email, 'password': user.password, 'created_at': user.created_at})
    return jsonify(user_list)


@bp.route("/register", methods=["POST"])
def register():
    email = request.json.get("email")
    password = request.json.get("password")

    # check if email and password are not empty
    if not email or not password:
        return jsonify({
            'success': False,
            'message': 'email and password are required',
            'status': 400}), 400
    
    # check if user already exists
    existing_user = User.query.filter_by(email = email).first()
    if existing_user:
        return jsonify({
            'success': False,
            'message': 'user already registered',
            'status': 400}), 400
    
    # create new user
    new_user = User(email = email)
    new_user.set_password(password)
    db.session.add(new_user)
    db.session.commit()

    # create session
    session = Session(user_id=new_user.id)
    db.session.add(session)
    db.session.commit()

    # return registration success
    return jsonify({
        'success': True,
        'message': 'user registered successfully',
        'status': 200,
        'user': {'token': session.token,
                'userId': new_user.id,
                'email': new_user.email}}), 200

@bp.route("/login", methods=["POST"])
def login():
    # empty data check
    email = request.json.get("email")
    password = request.json.get("password")
    if not email or not password:
        return {"status": "400",
                "message": "missing email or password"}, 400
    
    email = request.json.get("email")
    password = request.json.get("password")

    user = User.query.filter_by(email=email).first()
    # check if user credentials are valid
    if not user or not user.check_password(password):
        return {"status": "401",
                "message": "invalid email or password"}, 401
    
    # if not user or not user.password:
    #     return {"status": "401",
    #             "message": "invalid email or password"}, 401

    # create token on login
    session = Session(user_id=user.id)
    db.session.add(session)
    db.session.commit()

    return {"status": "200",
                "message": "login successful",
                "token": session.token}, 200

@bp.route("/logout", methods=["DELETE"])
def logout():

    # user_token = request.json.get("token")
    # get the session id from session table
    # token = session.get('token')
    token = request.json.get("token")

    # check if the session exists in the database
    session_obj = Session.query.filter_by(token=token).first()
    if session_obj:
        db.session.delete(session_obj)
        db.session.commit()

    # remove the user_id key from session
    # session.pop('user_id', None)
    return {
        "status": "200",
        "message": "logout successful",
    }, 200

@bp.route("/send_otp", methods=["POST"])
def send_otp():
    email = request.json.get("email")
    # email = "gavinrockgomes@gmail.com"
    # email = "dc20-52@ritgoa.ac.in"
    otp = generate_otp(email=email)
    send_otp_email(
        email_recipient=email,
        # recipient_name=name if user is None else user.name,
        recipient_name=email,
        otp=otp,
    )
    return jsonify({
        'status': '200',
        'message': 'otp sent successfully'})


# init dict to store verified emails and their OTP status
verified_emails = {}

@bp.route("/verify_otp", methods=["POST"])
def verify_otp_email():
    email = request.json.get('email')
    otp = request.json.get('otp')
    print(email, otp)

    # check if email is already verified
    if email in verified_emails:
        if verified_emails[email] == True:
            return jsonify({'success': False, 'message':'Email already verified', 'wrong_otp': False, 'status': 400}), 400

    # verify the OTP
    verified = verify_otp(email=email, otp=otp)

    if verified is False:
        return jsonify({'success': False, 'message':'OTP incorrect', 'wrong_otp': True, 'status': 400}), 400
    
    # mark the email as verified
    verified_emails[email] = True

    return jsonify({
        'success': True,
        'message': 'otp correct',
        'status': 200}), 200