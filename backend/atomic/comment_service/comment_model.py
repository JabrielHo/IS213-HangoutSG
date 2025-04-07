import uuid
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import pytz

db = SQLAlchemy()
singapore_tz = pytz.timezone('Asia/Singapore')

class Comment(db.Model):
    __tablename__ = "comments"

    comment_id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    parent_id = db.Column(db.String(36), nullable=True)
    post_id = db.Column(db.String(36), nullable=False)
    author_id = db.Column(db.String(50), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(singapore_tz))
    status = db.Column(db.String(20), default="published")

    def json(self):
        return {
            "comment_id": self.comment_id,
            "parent_id": self.parent_id,
            "post_id": self.post_id,
            "author_id": self.author_id,
            "content": self.content,
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            "status": self.status
        }
