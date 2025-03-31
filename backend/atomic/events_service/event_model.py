from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
import os
import uuid

load_dotenv()

app = Flask(__name__)
CORS(app)

# Docker
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")

db = SQLAlchemy(app)

class Event(db.Model):
    __tablename__ = 'events'
    event_id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    community_id = db.Column(db.String(36), nullable=False)
    organizer_id = db.Column(db.String(50), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=False)
    location = db.Column(db.String(255), nullable=False)
    event_date = db.Column(db.DateTime, nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    capacity = db.Column(db.Integer, nullable=False)

@app.route('/events', methods=['POST'])
def create_event():
    data = request.json
    new_event = Event(
        community_id=data.get('community_id'),
        organizer_id=data.get('organizer_id'),
        title=data.get('title'),
        description=data.get('description'),
        location=data.get('location'),
        event_date=data.get('event_date'),
        capacity=data.get('capacity')
    )
    try:
        db.session.add(new_event)
        db.session.commit()
        return jsonify({'message': 'Event created', 'event_id': new_event.event_id}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/events/<event_id>', methods=['DELETE'])
def delete_event(event_id):
    try:
        event = Event.query.get(event_id)
        if not event:
            return jsonify({'error': 'Event not found'}), 404
        db.session.delete(event)
        db.session.commit()
        return jsonify({'message': 'Event deleted'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5004)
    
