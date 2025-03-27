from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import pytz
import uuid

db = SQLAlchemy()

singapore_tz = pytz.timezone("Asia/Singapore")

class Email(db.Model):
    __tablename__ = "emails"
    
    email_id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(50), nullable=False)
    to_email = db.Column(db.String(255), nullable=False) 
    subject = db.Column(db.String(255), nullable=False)
    body = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(singapore_tz).replace(tzinfo=None))
    
    def __init__(self, user_id, to_email, subject, body):
        self.user_id = user_id
        self.to_email = to_email
        self.subject = subject
        self.body = body

    def json(self):
        return {
            "email_id": self.email_id,
            "user_id": self.user_id,
            "to_email": self.to_email,
            "subject": self.subject,
            "body": self.body,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
