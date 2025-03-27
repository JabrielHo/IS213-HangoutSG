import uuid
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import pytz

db = SQLAlchemy()
singapore_tz = pytz.timezone('Asia/Singapore')

class Post(db.Model):
    __tablename__ = "posts"

    post_id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    community_id = db.Column(db.String(36), nullable=False)
    author_id = db.Column(db.String(50), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    content = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(singapore_tz))
    status = db.Column(db.String(20), default="published")