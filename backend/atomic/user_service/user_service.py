from flask import Flask, request, jsonify
from flask_cors import CORS
from user_model import db, User
import re
from dotenv import load_dotenv
import os

# Initialize Flask app
app = Flask(__name__)
CORS(app)

email_pattern = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")

# Database config
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Initialize SQLAlchemy
db.init_app(app)

with app.app_context():
    db.create_all()


# Register user
@app.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    if (
        not data
        or "username" not in data
        or "email" not in data
        or "password" not in data
    ):
        return jsonify({"message": "Username, email and password required"}), 400

    if User.query.filter_by(username=data["username"]).first():
        return jsonify({"message": "Username already exists"}), 400

    if User.query.filter_by(email=data["email"]).first():
        return jsonify({"message": "Email already exists"}), 400

    # Email format validation
    if not email_pattern.match(data["email"]):
        return jsonify({"message": "Invalid email format"}), 400

    if len(data["password"]) < 8:
        return jsonify({"message": "Password must be at least 8 characters"}), 400

    user = User(
        username=data["username"], email=data["email"], role=data.get("role", "user")
    )
    user.set_password(data["password"])
    db.session.add(user)
    db.session.commit()

    return jsonify(user.to_dict()), 201


# Login user
@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()

    # Input validation
    if not data or "email" not in data or "password" not in data:
        return jsonify({"message": "Email and password required"}), 400

    user = User.query.filter_by(email=data["email"]).first()

    if user and user.check_password(data["password"]):
        return jsonify({"message": "Login successful", "user": user.to_dict()}), 200

    return jsonify({"message": "Invalid credentials"}), 401


# Get user by ID
@app.route("/users/<string:user_id>", methods=["GET"])
def get_user(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({"message": "User not found"}), 404

    return jsonify(user.to_dict()), 200


# Update user profile
@app.route("/users/<string:user_id>", methods=["PUT"])
def update_user(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({"message": "User not found"}), 404

    data = request.get_json()
    if "username" in data:
        user.username = data["username"]
    if "email" in data:
        user.email = data["email"]
    if "profile_pic_url" in data:
        user.profile_pic_url = data["profile_pic_url"]
    if "password" in data:
        user.set_password(data["password"])

    db.session.commit()
    return jsonify(user.to_dict()), 200


# Delete user
@app.route("/users/<string:user_id>", methods=["DELETE"])
def delete_user(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({"message": "User not found"}), 404

    db.session.delete(user)
    db.session.commit()
    return jsonify({"message": "User deleted"}), 200


# Start Flask app
if __name__ == "__main__":
    app.run(port=5000, debug=True)
