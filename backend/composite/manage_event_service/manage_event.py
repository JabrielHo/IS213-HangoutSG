from flask import Flask, request, jsonify
import requests
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# Configuration
EVENTS_SERVICE_URL = os.getenv("EVENTS_SERVICE_URL", "http://localhost:5004")

class EventsServiceClient:
    """Client for interacting with the atomic events microservice"""
    
    def __init__(self, base_url):
        self.base_url = base_url
        
    def create_event(self, event_data):
        """Create a new event by calling the atomic service"""
        response = requests.post(f"{self.base_url}/events", json=event_data)
        return response.json(), response.status_code
        
    def delete_event(self, event_id):
        """Delete an event by calling the atomic service"""
        response = requests.delete(f"{self.base_url}/events/{event_id}")
        return response.json(), response.status_code
        
    def get_event(self, event_id):
        """Get event by ID from the atomic service"""
        response = requests.get(f"{self.base_url}/events/{event_id}")
        return response.json(), response.status_code
        
    def get_all_events(self):
        """Get all events from the atomic service"""
        response = requests.get(f"{self.base_url}/events")
        return response.json(), response.status_code
        
    def get_events_by_organizer(self, organizer_id):
        """Get events by organizer ID from the atomic service"""
        response = requests.get(f"{self.base_url}/events/organizer/{organizer_id}")
        return response.json(), response.status_code

# Initialize client
events_client = EventsServiceClient(EVENTS_SERVICE_URL)

@app.route("/api/events", methods=["POST"])
def create_event():
    """Composite endpoint to create an event"""
    event_data = request.json
    
    # Validate required fields
    required_fields = ["community_id", "organizer_id", "title", "event_date"]
    for field in required_fields:
        if field not in event_data:
            return jsonify({"error": f"Missing required field: {field}"}), 400
    
    # Optional field defaults or transformations could be added here
    
    # Call atomic service
    result, status_code = events_client.create_event(event_data)
    
    return jsonify(result), status_code

@app.route("/api/events/<event_id>", methods=["DELETE"])
def delete_event(event_id):
    """Composite endpoint to delete an event"""
    # First, verify the event exists
    event_result, event_status = events_client.get_event(event_id)
    
    if event_status != 200:
        return jsonify(event_result), event_status
    
    # Call atomic service to delete
    result, status_code = events_client.delete_event(event_id)
    
    return jsonify(result), status_code

@app.route("/api/events", methods=["GET"])
def get_events():
    """Composite endpoint to get all events"""
    result, status_code = events_client.get_all_events()
    return jsonify(result), status_code

@app.route("/api/events/<event_id>", methods=["GET"])
def get_event(event_id):
    """Composite endpoint to get an event by ID"""
    result, status_code = events_client.get_event(event_id)
    return jsonify(result), status_code

@app.route("/api/events/organizer/<organizer_id>", methods=["GET"])
def get_events_by_organizer(organizer_id):
    """Composite endpoint to get events by organizer ID"""
    result, status_code = events_client.get_events_by_organizer(organizer_id)
    return jsonify(result), status_code

@app.errorhandler(Exception)
def handle_exception(e):
    """Global exception handler"""
    app.logger.error(f"Error: {str(e)}")
    return jsonify({"error": "Internal Server Error"}), 500

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5009))
    debug = os.getenv("DEBUG", "False").lower() == "true"
    app.run(port=port, debug=debug)