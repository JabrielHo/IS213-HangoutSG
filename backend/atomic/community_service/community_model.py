from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import pytz

db = SQLAlchemy()

singapore_tz = pytz.timezone('Asia/Singapore')

class Community(db.Model):
    __tablename__ = 'communities'
    
    community_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)
    description = db.Column(db.Text, nullable=False)
    creator_id = db.Column(db.String(50), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(singapore_tz).replace(tzinfo=None))
    
    def __init__(self, name, description, creator_id):
        self.name = name
        self.description = description
        self.creator_id = creator_id
        
    def json(self):
        return {
            'community_id': self.community_id,
            'name': self.name,
            'description': self.description,
            'creator_id': self.creator_id,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }