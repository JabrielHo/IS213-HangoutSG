from flask import Flask, request, jsonify
import requests
import os
from dotenv import load_dotenv
import pika
import json
from flask_cors import CORS

load_dotenv()

app = Flask(__name__)
CORS(app)


# Configuration
OUTSYSTEM_URL = f"https://personal-iw6ceuuv.outsystemscloud.com/Community_members/rest/CommunityMemberAPI/membersbycommunity/"
EVENTS_SERVICE_URL = os.getenv("EVENTS_SERVICE_URL", "http://localhost:5004")
REGISTRATION_URL = f"http://localhost:5005/api/registrations/event/"

class EventsServiceClient:
    """Client for interacting with the atomic events microservice"""
    
    def __init__(self, base_url):
        self.base_url = base_url
        
    def create_event(self, event_data):
        """Create a new event by calling the atomic service"""
        response = requests.post(f"{self.base_url}/api/events", json=event_data)
        return response.json(), response.status_code
        
    def delete_event(self, event_id):
        """Delete an event by calling the atomic service"""
        response = requests.delete(f"{self.base_url}/api/events/{event_id}")
        return response.json(), response.status_code
    
    def validate_location(self, postal_code): 
        """Validates location and returns formatted address or error"""
        url = f"https://www.onemap.gov.sg/api/common/elastic/search?searchVal={postal_code}&returnGeom=Y&getAddrDetails=Y"
        
        try:
            response = requests.get(url)
            response.raise_for_status()  # Ensure status code is 200
        except requests.exceptions.RequestException as e:
            return {"error": str(e)}, 500  # Return 500 if there was an issue with the request

        data = response.json()
        
        if data.get("found", 0) == 0:
            return {"error": "Bad address"}, 400  # Return 400 for a bad address

        # Loop through the results to check if any postal code matches
        for result in data["results"]:
            if result.get("POSTAL") == postal_code:
                address = f"{result['BLK_NO']} {result['ROAD_NAME']}, Singapore {result['POSTAL']}"
                return address  # Return address if postal code matches

        # If no match is found, return error
        return {"error": "Postal code not found in results"}, 404

    
    def publish_to_inbox(message):
        try:
            amqp_host = os.getenv("RABBITMQ_HOST", "localhost")
            amqp_port = os.getenv("RABBITMQ_PORT", 5672)
            exchange_name = os.getenv("EXCHANGE_NAME", "hangout_exchange")
            routing_key = os.getenv("ROUTING_KEY", "inbox_message")

            connection = pika.BlockingConnection(
                pika.ConnectionParameters(host=amqp_host, port=amqp_port)
            )
            channel = connection.channel()

            # Convert message to JSON and publish
            message_json = json.dumps(message)
            channel.basic_publish(
                exchange=exchange_name,
                routing_key=routing_key,
                body=message_json,
                properties=pika.BasicProperties(
                    delivery_mode=2,
                ),
            )

            connection.close()
        except Exception as e:
            print(f"Error publishing message to inbox: {e}")
            

# Initialize client
events_client = EventsServiceClient(EVENTS_SERVICE_URL)

@app.route("/api/events", methods=["POST"])
def create_event():
    """Composite endpoint to create an event"""
    event_data = request.json
    
    # Validate required fields
    required_fields = ["community_id", "organizer_id", "title", "event_date", "location", "description", "capacity"]
    for field in required_fields:
        if field not in event_data:
            return jsonify({"error": f"Missing required field: {field}"}), 400
        
    # Get event details
    subject = event_data["title"]
    content = event_data["description"]
    community_id = event_data["community_id"]
    postal_code = event_data["location"]

    # Validate location
    location = events_client.validate_location(postal_code)
    if isinstance(location, dict) and location.get("error"):  # Error in location validation
        return jsonify(location), 400
    
    event_data["location"] = location
    
    # get user_ID from community
    response = requests.get(OUTSYSTEM_URL + community_id)

    # Check if request was successful
    if response.status_code == 200:
        data = response.json()

        # Extract user IDs
        user_id = [member["user_id"] for member in data.get("CommunityMemberAPI", [])]
    else:
        return jsonify(response.text), response.status_code

    # Publish notification message to inbox
    inbox_message = {
        "type": "event_creation",
        "receiver_ids": user_id,
        "subject": "There is a new event => " + subject,
        "content": "This is the description of the event => " + content,
    }

    EventsServiceClient.publish_to_inbox(inbox_message)

    # Call atomic service
    result, status_code = events_client.create_event(event_data)
    
    return jsonify(result), status_code

@app.route("/api/events/<event_id>", methods=["DELETE"])
def delete_event(event_id):
    """Composite endpoint to delete an event"""
    # Step 1: Check event details and capacity
    event_response = requests.get(f"{EVENTS_SERVICE_URL}/api/events/{event_id}")
    if event_response.status_code != 200:
        return jsonify({"error": "Event not found"}), 404

    event = event_response.json()
    subject = event["title"]
    content = event["description"]

    
    # get user_ID from event_registration
    user_id = []
    response = requests.get(REGISTRATION_URL + event_id)

    if response.status_code == 200:
        data = response.json()
        user_id = [registration["user_id"] for registration in data.get("registrations", [])]
    else:
        return jsonify({"error": f"Request failed with status {response.status_code}", "message": response.text})


    # Publish notification message to inbox
    inbox_message = {
        "type": "event_deletion",
        "receiver_ids": user_id,
        "subject": "Deletion of " + subject,
        "content": content,
    }

    EventsServiceClient.publish_to_inbox(inbox_message)
    
    # Call atomic service to delete
    result, status_code = events_client.delete_event(event_id)
    
    return jsonify(result), status_code

@app.errorhandler(Exception)
def handle_exception(e):
    """Global exception handler"""
    app.logger.error(f"Error: {str(e)}")
    return jsonify({"error": "Internal Server Error"}), 500

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5009)