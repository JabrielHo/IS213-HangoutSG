from flask import Flask, request, jsonify
import requests
import pika
import uuid

app = Flask(__name__)

# Function to validate location with Google Maps API
def validate_location(address):
    GOOGLE_MAPS_API_KEY = "your_google_maps_api_key"
    url = f"https://maps.googleapis.com/maps/api/geocode/json?address={address}&key={GOOGLE_MAPS_API_KEY}"
    response = requests.get(url)
    data = response.json()
    return "results" in data and len(data["results"]) > 0

# RabbitMQ Connection Setup
def send_to_inbox(event_data):
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()
    channel.queue_declare(queue='event_inbox')
    
    channel.basic_publish(exchange='',
                          routing_key='event_inbox',
                          body=str(event_data))
    connection.close()

# Endpoint to create an event
@app.route('/events', methods=['POST'])
def create_event():
    data = request.json
    
    if not validate_location(data.get("location")):
        return jsonify({"error": "Invalid location"}), 400
    
    event_id = str(uuid.uuid4())
    event_data = {
        "event_id": event_id,
        "title": data["title"],
        "description": data.get("description", ""),
        "location": data["location"],
        "event_date": data["event_date"],
        "organizer_id": data["organizer_id"]
    }
    
    # Save to database (Assuming SQLAlchemy or other DB integration)
    # db.session.add(Event(**event_data))
    # db.session.commit()
    
    # Send message to the inbox service
    send_to_inbox(event_data)
    
    return jsonify({"message": "Event created successfully", "event_id": event_id})

if __name__ == '__main__':
    app.run(debug=True)
