from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import UniqueConstraint
import uuid
from datetime import datetime

db = SQLAlchemy()

class EventRegistration(db.Model):
    __tablename__ = 'event_registrations'
    
    registration_id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    event_id = db.Column(db.String(36), nullable=False)
    user_id = db.Column(db.String(50), nullable=False)
    registered_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # This enforces uniqueness at the database level
    __table_args__ = (
        UniqueConstraint('event_id', 'user_id', name='uix_event_user'),
    )
    
    def __init__(self, event_id, user_id):
        self.event_id = event_id
        self.user_id = user_id
        
    def json(self):
        return {
            "registration_id": self.registration_id,
            "event_id": self.event_id,
            "user_id": self.user_id,
            "registered_at": self.registered_at.isoformat()
        }