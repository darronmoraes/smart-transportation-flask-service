from flask import Blueprint, jsonify, request
import json
from models.user import User
from models.session import Session
from db import db


bp = Blueprint("user", __name__, url_prefix="/user")

@bp.route("/user", methods=["GET", "POST"])
def user():
    users = User.query.all()
    user_list = []
    for user in users:
        user_list.append({'id': user.id, 'username': user.username, 'password': user.password, 'created_at': user.created_at})
    return jsonify(user_list)

@bp.route("/register", methods=["POST"])
def register():
    username = request.json.get("username")
    password = request.json.get("password")
    existing_user = User.query.filter_by(username = username).first()
    if existing_user:
        return jsonify({'message': 'username already registered'}), 400
    new_user = User(username = username)
    new_user.set_password(password)
    db.session.add(new_user)
    db.session.commit()
    # create session
    session = Session(user_id=new_user.id)
    db.session.add(session)
    db.session.commit()
    return jsonify({
        'message': 'user registered successfully', 
        'token': session.token, 
        'user': {
            'id': new_user.id,
            'username': new_user.username
        }
        })

bp = Blueprint("user", __name__, url_prefix="/admin")

"""
route to get admin as user data
"""
# @bp.route("/admin", methods=["GET", "POST"])
# def user():
#     users = User.query.all()
#     admin_list = []
#     for user in users:
#         admin_list.append({'id': user.id, 'username': user.username, 'password': user.password, 'created_at': user.created_at})
#     return jsonify(admin_list)


"""
route to register admin as user
"""
@bp.route("/register-admin", methods=["POST"])
def admin_register():
    username = request.json.get("username")
    password = request.json.get("password")
    existing_user = User.query.filter_by(username = username).first()
    if existing_user:
        return jsonify({'message': 'username already registered'}), 400
    new_user = User(username = username)
    new_user.set_password(password)
    db.session.add(new_user)
    db.session.commit()
    # create session
    session = Session(user_id=new_user.id)
    db.session.add(session)
    db.session.commit()
    return jsonify({
        'message': 'admin registered successfully', 
        'token': session.token, 
        'admin': {
            'id': new_user.id,
            'username': new_user.username
        }
        })
