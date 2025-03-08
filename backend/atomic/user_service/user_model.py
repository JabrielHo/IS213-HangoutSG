from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
import pytz
import uuid

db = SQLAlchemy()

singapore_tz = pytz.timezone('Asia/Singapore')


class User(db.Model):
    __tablename__ = "users"

    user_id = db.Column(
        db.String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    profile_pic_url = db.Column(db.String(255), default=None)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(singapore_tz))
    role = db.Column(db.String(20), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            "user_id": self.user_id,
            "username": self.username,
            "email": self.email,
            "profile_pic_url": self.profile_pic_url,
            "created_at": self.created_at.isoformat(),
            "role": self.role,
        }
