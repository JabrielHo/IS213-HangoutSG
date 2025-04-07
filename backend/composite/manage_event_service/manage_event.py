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
EVENTS_SERVICE_URL = os.getenv("EVENTS_SERVICE_URL", "http://localhost:5004")
OUTSYSTEM_URL = f"https://personal-iw6ceuuv.outsystemscloud.com/Community_members/rest/CommunityMemberAPI/membersbycommunity/"

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
    required_fields = ["community_id", "organizer_id", "title", "event_date"]
    for field in required_fields:
        if field not in event_data:
            return jsonify({"error": f"Missing required field: {field}"}), 400
        
    #get details
    subject = event_data["title"]
    content = event_data["description"]
    community_id = event_data["community_id"]
    
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
    event_response = requests.get(f"{EVENTS_SERVICE_URL}/events/{event_id}")
    if event_response.status_code != 200:
        return jsonify({"error": "Event not found"}), 404

    event = event_response.json()
    subject = event["title"]
    content = event["description"]
    community_id = event["community_id"]

    
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