from datetime import datetime
from db import db
from flask import Flask, jsonify, request
from flask_mysqldb import MySQL
from flask_marshmallow import Marshmallow
from flask_cors import CORS

from resources.user import bp as UserBluprint

app = Flask(__name__)

marshmallow = Marshmallow()
mysql = MySQL(app)

CORS(app)

# # User class
# class User(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     username = db.Column(db.String(45), nullable=False)
#     password = db.Column(db.String(45), nullable=False)
#     created_at = db.Column(db.DateTime, default=datetime.utcnow)

#     def __init__(self, username, password):
#         self.username = username
#         self.password = password


# Schema
# class UserSchema(marshmallow.Schema):
#     class Meta:
#         fields = ('id', 'username', 'password', 'created_at')

# user_schema = UserSchema()
# users_schema = UserSchema(many=True)

# connect db
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:root@localhost/sts_test'
db.init_app(app)

# Secret Key
# app.config['SECRET_KEY'] = 'smarttransportationsystem2023'

# @app.route('/user/add', methods=['POST'])
# def add_user():
#     _json = request.json
#     username = _json['username']
#     password = _json['password']
#     new_user = User(username=username, password=password)
#     db.session.add(new_user)
#     db.session.commit()
#     return jsonify({'Message':'User added'})


# @app.route('/user', methods=['GET'])
# def get_user():
#     user = []
#     data = User.query.all()
#     users = users_schema.dump(data)
#     return jsonify(users)


app.register_blueprint(UserBluprint)


if __name__ == '__main__':
    # app.run(debug=True)
    # app.run(host='192.168.0.112', debug=True)
    # run on all ip addresses
    app.run(host='0.0.0.0', debug=True)