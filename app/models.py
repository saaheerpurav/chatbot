from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.ext.mutable import MutableList

from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()

class Leads(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    bot_id = db.Column(db.String(10), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now, nullable=False)

    def __repr__(self):
        return f'<Lead {self.email}, bot: {self.bot_id}>'
    

class Users(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(250), nullable=False)
    bot_ids = db.Column(MutableList.as_mutable(ARRAY(db.String)), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.now, nullable=False)

    def __repr__(self):
        return f'<User {self.email}>'