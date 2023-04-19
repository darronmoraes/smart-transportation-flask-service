from flask import jsonify, request
from functools import wraps
from db import db

# import session model
from models.session import Session

# middleware to handle authentication for a user
def auth_middleware(next_handler):
    @wraps(next_handler)
    def middleware(request):
        token = request.headers.get('Authorization')
        if not token or not is_valid_token(token):
            return jsonify({
                'success': True,
                'message': 'user token is invalid',
                'status': 401 }), 401
        return next_handler(request)
    return middleware



# function to check if user session is valid
def is_valid_token(token):
    session = Session.query.filter_by(Session.token == token).first()
    if session is not None:  # return True if session is valid
        return True
    return False