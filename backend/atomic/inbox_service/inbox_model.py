from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import pytz
import uuid

db = SQLAlchemy()

singapore_tz = pytz.timezone('Asia/Singapore')

class InboxMessage(db.Model):
    __tablename__ = "inbox"

    message_id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    receiver_id = db.Column(db.String(50), nullable=False)
    subject = db.Column(db.String(255), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(singapore_tz))
    status = db.Column(db.String(20), default="unread")