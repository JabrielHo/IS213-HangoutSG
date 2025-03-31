from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
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

db = SQLAlchemy(app)

#user registering a event
@app.route('/api/registrations', methods=['POST'])
def create_registration():
    try:
        data = request.get_json()
        
        # Validate required fields
        if not all(k in data for k in ['event_id', 'user_id']):
            return jsonify({
                "message": "Missing required fields - event_id and user_id are required"
            }), 400
        
        event_id = data['event_id']
        user_id = data['user_id']
        
        # Create new registration
        registration = EventRegistration(event_id=event_id, user_id=user_id)
        
        db.session.add(registration)
        db.session.commit()
        
        return jsonify({
            "message": "Registration successful",
            "data": registration.json()
        }), 201
        
    except IntegrityError:
        db.session.rollback()
        return jsonify({
            "message": "User is already registered for this event"
        }), 409
    
    except Exception as e:
        db.session.rollback()
        return jsonify({
            "message": f"An error occurred: {str(e)}"
        }), 500
    

#get all events of user

if __name__ == '__main__':
    app.run(debug=True, port=5005
)
    

