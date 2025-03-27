from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import pytz
import uuid

db = SQLAlchemy()

singapore_tz = pytz.timezone('Asia/Singapore')

class ContentModeration(db.Model):
    __tablename__ = 'flagged'
    
    flag_id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    post_id = db.Column(db.String(36), nullable=True)
    comment_id = db.Column(db.String(36), nullable=True)
    flagged_by = db.Column(db.String(50), nullable=False)
    reason = db.Column(db.String(255), nullable=False)
    status = db.Column(db.String(20), nullable=False, default='pending')
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now(singapore_tz))
    
    def __init__(self, flagged_by, reason, status='pending', post_id=None, comment_id=None):
        if (post_id and comment_id) or (not post_id and not comment_id):
            raise ValueError("You must flag either a post or a comment, not both or neither.")
        self.post_id = post_id
        self.comment_id = comment_id
        self.flagged_by = flagged_by
        self.reason = reason
        self.status = status
        
    def json(self):
        return {
            'flag_id': self.flag_id,
            'post_id': self.post_id,
            'comment_id': self.comment_id,
            'flagged_by': self.flagged_by,
            'reason': self.reason,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
