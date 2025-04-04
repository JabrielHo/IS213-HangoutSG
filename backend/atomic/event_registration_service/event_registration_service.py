from flask import Flask, request, jsonify
from sqlalchemy.exc import IntegrityError
import os
from flask_cors import CORS
from dotenv import load_dotenv
from event_registration_model import db, EventRegistration

load_dotenv()

app = Flask(__name__)
CORS(app)

# Docker
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")

db.init_app(app)


# user registering a event
@app.route("/api/registrations", methods=["POST"])
def create_registration():
    try:
        data = request.get_json()

        # Validate required fields
        if not all(k in data for k in ["event_id", "user_id"]):
            return (
                jsonify(
                    {
                        "message": "Missing required fields - event_id and user_id are required"
                    }
                ),
                400,
            )

        event_id = data["event_id"]
        user_id = data["user_id"]

        # Create new registration
        registration = EventRegistration(event_id=event_id, user_id=user_id)

        db.session.add(registration)
        db.session.commit()

        return (
            jsonify(
                {"message": "Registration successful", "data": registration.json()}
            ),
            201,
        )

    except IntegrityError:
        db.session.rollback()
        return jsonify({"message": "User is already registered for this event"}), 409

    except Exception as e:
        db.session.rollback()
        return jsonify({"message": f"An error occurred: {str(e)}"}), 500


# Get all events of user
@app.route("/api/registrations/<user_id>", methods=["GET"])
def get_user_events(user_id):
    try:
        registrations = EventRegistration.query.filter_by(user_id=user_id).all()

        if not registrations:
            return jsonify({"message": "No events found for this user"}), 404

        events = [reg.json() for reg in registrations]

        return jsonify({"events": events}), 200

    except Exception as e:
        return jsonify({"message": f"An error occurred: {str(e)}"}), 500


# Get all registrations for an event
@app.route("/api/registrations/event/<event_id>", methods=["GET"])
def get_event_registrations(event_id):
    try:
        registrations = EventRegistration.query.filter_by(event_id=event_id).all()

        result = {
            "event_id": event_id,
            "registrations": [reg.json() for reg in registrations],
            "count": len(registrations),
        }

        return jsonify(result), 200

    except Exception as e:
        return jsonify({"message": f"An error occurred: {str(e)}"}), 500

# Check if user is registered for an event
@app.route("/api/registrations/check", methods=["POST"])
def check_registration():
    try:
        data = request.get_json()
        
        if not data or "event_id" not in data or "user_id" not in data:
            return (
                jsonify(
                    {
                        "message": "Missing required fields - event_id and user_id are required"
                    }
                ),
                400,
            )

        event_id = data["event_id"]
        user_id = data["user_id"]

        registration = EventRegistration.query.filter_by(
            event_id=event_id, user_id=user_id
        ).first()

        if registration:
            return (
                jsonify({"registered": True, "registration": registration.json()}),
                200,
            )
        else:
            return jsonify({"registered": False}), 200

    except Exception as e:
        return jsonify({"message": f"An error occurred: {str(e)}"}), 500

if __name__ == "__main__":
    app.run(debug=True, port=5005)
