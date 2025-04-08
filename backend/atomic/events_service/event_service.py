from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import os
from event_model import db, Event
from datetime import datetime

load_dotenv()

app = Flask(__name__)
CORS(app)

app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

@app.route("/api/events", methods=["POST"])
def create_event():
    data = request.json
    new_event = Event(
        community_id=data.get("community_id"),
        organizer_id=data.get("organizer_id"),
        title=data.get("title"),
        description=data.get("description"),
        location=data.get("location"),
        event_date=data.get("event_date"),
        capacity=data.get("capacity"),
    )
    try:
        db.session.add(new_event)
        db.session.commit()
        return (
            jsonify({"message": "Event created", "event_id": new_event.event_id}),
            201,
        )
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@app.route("/api/events/<event_id>", methods=["DELETE"])
def soft_delete_event(event_id):
    try:
        event = db.session.get(Event, event_id)
        if not event or event.is_deleted:
            return jsonify({"error": "Event not found"}), 404

        event.is_deleted = True
        db.session.commit()
        return jsonify({"message": "Event soft deleted"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500



@app.route("/api/events", methods=["GET"])
def get_events():
    try:
        # Get current date for comparison
        current_date = datetime.now()
        
        # Filter events that haven't passed yet
        events = Event.query.filter_by(is_deleted=False).filter(Event.event_date >= current_date).all()
        
        events_list = [
            {
                "event_id": event.event_id,
                "community_id": event.community_id,
                "organizer_id": event.organizer_id,
                "title": event.title,
                "description": event.description,
                "location": event.location,
                "event_date": event.event_date,
                "created_at": event.created_at,
                "capacity": event.capacity,
            }
            for event in events
        ]

        return jsonify({"events": events_list}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# get all events by organizer_id
@app.route("/api/events/organizer/<organizer_id>", methods=["GET"])
def get_events_by_organizer(organizer_id):
    try:
        events = Event.query.filter_by(
            organizer_id=organizer_id, is_deleted=False
        ).all()
        events_list = [
            {
                "event_id": event.event_id,
                "community_id": event.community_id,
                "organizer_id": event.organizer_id,
                "title": event.title,
                "description": event.description,
                "location": event.location,
                "event_date": event.event_date,
                "created_at": event.created_at,
                "capacity": event.capacity,
            }
            for event in events
        ]

        return jsonify({"events": events_list}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/events/<event_id>", methods=["GET"])
def get_event(event_id):
    """Get event information by event ID"""
    try:
        event = db.session.get(Event, event_id)

        if not event or event.is_deleted:
            return jsonify({"error": "Event not found"}), 404

        event_data = {
            "event_id": event.event_id,
            "community_id": event.community_id,
            "organizer_id": event.organizer_id,
            "title": event.title,
            "description": event.description,
            "location": event.location,
            "event_date": event.event_date,
            "created_at": event.created_at,
            "capacity": event.capacity,
        }

        return jsonify(event_data), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@app.route("/api/events/community/<community_id>", methods=["GET"])
def get_events_by_community(community_id):
    """Get all events by community ID"""
    try:

        # Get current date for comparison
        current_date = datetime.now()

        events = db.session.query(Event).filter_by(community_id=community_id, is_deleted=False).filter(Event.event_date >= current_date).all()

        # Return empty array instead of 404
        events_data = [
            {
                "event_id": event.event_id,
                "community_id": event.community_id,
                "organizer_id": event.organizer_id,
                "title": event.title,
                "description": event.description,
                "location": event.location,
                "event_date": event.event_date,
                "created_at": event.created_at,
                "capacity": event.capacity,
            }
            for event in events
        ]

        return jsonify(events_data), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5004)
