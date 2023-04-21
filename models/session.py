from datetime import datetime
from db import db

import hashlib

from models.user import User


class Session(db.Model):
    __tablename__ = 'session'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey(User.id), nullable=False)
    token = db.Column(db.String(500), nullable=False, unique=True, default=lambda u=user_id: hashlib.md5(
        "-".join([str(u), str(datetime.utcnow().timestamp())]).encode("utf-8")
    ).hexdigest())
    start_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    ip_address = db.Column(db.String(100), nullable=True)