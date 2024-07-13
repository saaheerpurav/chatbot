from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Leads(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    bot_id = db.Column(db.String(10), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now, nullable=False)

    def __repr__(self):
        return f'<Lead {self.name}, {self.email}, bot: {self.bot_id}>'