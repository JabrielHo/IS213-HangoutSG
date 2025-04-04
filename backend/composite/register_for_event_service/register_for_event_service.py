from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import os
import requests
import json
import pika

app = Flask(__name__)
CORS(app)
load_dotenv()

# Service URLs
EVENT_SERVICE_URL = os.environ.get("EVENT_SERVICE_URL", "http://localhost:5004")
EVENT_REGISTRATION_SERVICE_URL = os.environ.get(
    "EVENT_REGISTRATION_SERVICE_URL", "http://localhost:5005"
)

# RabbitMQ configuration
RABBITMQ_HOST = os.environ.get("RABBITMQ_HOST", "localhost")
RABBITMQ_PORT = int(os.environ.get("RABBITMQ_PORT", 5672))
EXCHANGE_NAME = os.environ.get("EXCHANGE_NAME", "hangout_exchange")
INBOX_ROUTING_KEY = os.environ.get("ROUTING_KEY", "inbox_message")
REGISTRATION_ROUTING_KEY = os.environ.get(
    "REGISTRATION_ROUTING_KEY", "event_registration"
)


def publish_to_inbox(message):
    """Publish message to RabbitMQ for inbox service"""
    try:
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(host=RABBITMQ_HOST, port=RABBITMQ_PORT)
        )
        channel = connection.channel()

        # Convert message to JSON and publish
        message_json = json.dumps(message)
        channel.basic_publish(
            exchange=EXCHANGE_NAME,
            routing_key=INBOX_ROUTING_KEY,
            body=message_json,
            properties=pika.BasicProperties(
                delivery_mode=2,  # Make message persistent
            ),
        )

        connection.close()
        return True
    except Exception as e:
        print(f"Error publishing message to inbox: {e}")
        return False


def publish_to_registration_queue(message):
    """Publish registration request to the event registration queue"""
    try:
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(host=RABBITMQ_HOST, port=RABBITMQ_PORT)
        )
        channel = connection.channel()

        # Ensure queue exists
        channel.queue_declare(queue="event_registration", durable=True)

        # Convert message to JSON and publish
        message_json = json.dumps(message)
        channel.basic_publish(
            exchange=EXCHANGE_NAME,
            routing_key=REGISTRATION_ROUTING_KEY,
            body=message_json,
            properties=pika.BasicProperties(
                delivery_mode=2,  # Make message persistent
            ),
        )

        connection.close()
        return True
    except Exception as e:
        print(f"Error publishing message to registration queue: {e}")
        return False


@app.route("/api/register", methods=["POST"])
def register_for_event():
    """API endpoint for clients to register for an event"""
    try:
        data = request.json
        if not data or "event_id" not in data or "user_id" not in data:
            return (
                jsonify({"error": "Missing required fields: event_id and user_id"}),
                400,
            )

        event_id = data["event_id"]
        user_id = data["user_id"]

        # Check if event exists first
        event_response = requests.get(f"{EVENT_SERVICE_URL}/events/{event_id}")
        if event_response.status_code != 200:
            return jsonify({"error": "Event not found"}), 404

        # Check if event registered already
        check_response = requests.post(
            f"{EVENT_REGISTRATION_SERVICE_URL}/api/registrations/check",
            json={"event_id": event_id, "user_id": user_id},
        )

        if check_response.status_code == 200:
            check_result = check_response.json()
            if check_result.get("registered"):
                return (
                    jsonify(
                        {
                            "success": False,
                            "message": "You are already registered for this event",
                        }
                    ),
                    409,
                )

        # Add registration request to the queue
        registration_data = {
            "event_id": event_id,
            "user_id": user_id,
        }

        queue_success = publish_to_registration_queue(registration_data)

        if queue_success:
            return (
                jsonify(
                    {
                        "success": True,
                        "message": "Your registration request has been received and is being processed. You will be notified of the outcome in your inbox shortly.",
                    }
                ),
                202,
            )
        else:
            return (
                jsonify(
                    {
                        "success": False,
                        "message": "Failed to submit registration request. Please try again later.",
                    }
                ),
                500,
            )

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/register_internal", methods=["POST"])
def process_registration():
    """Internal API endpoint to process registrations from the queue"""
    try:
        data = request.json
        if not data or "event_id" not in data or "user_id" not in data:
            return (
                jsonify({"error": "Missing required fields: event_id and user_id"}),
                400,
            )

        event_id = data["event_id"]
        user_id = data["user_id"]

        # Step 1: Check event details and capacity
        event_response = requests.get(f"{EVENT_SERVICE_URL}/events/{event_id}")
        if event_response.status_code != 200:
            return jsonify({"error": "Event not found"}), 404

        event = event_response.json()

        # Step 2: Get current registrations to check against capacity
        registrations_response = requests.get(
            f"{EVENT_REGISTRATION_SERVICE_URL}/api/registrations/event/{event_id}"
        )

        has_capacity = True
        registration_count = 0

        if registrations_response.status_code == 200:
            registration_data = registrations_response.json()
            registration_count = registration_data.get("count", 0)
            if registration_count >= event["capacity"]:
                has_capacity = False

        # Step 3: Register user if capacity allows
        registration_successful = False
        if has_capacity:
            registration_data = {"event_id": event_id, "user_id": user_id}
            registration_response = requests.post(
                f"{EVENT_REGISTRATION_SERVICE_URL}/api/registrations",
                json=registration_data,
            )

            if registration_response.status_code == 201:
                registration_successful = True
                result_message = "Successfully registered for the event"
            elif registration_response.status_code == 409:
                result_message = "You are already registered for this event"
            else:
                result_message = "Registration failed"
        else:
            result_message = (
                "Event has reached its maximum capacity. Please check again!"
            )

        # Step 4: Publish notification message to inbox
        inbox_message = {
            "type": "event_registration_outcome",
            "receiver_id": user_id,
            "subject": f"Event Registration: {event['title']}",
            "content": result_message,
        }
        publish_to_inbox(inbox_message)

        # Return response to queue processor
        if registration_successful:
            return (
                jsonify({"success": True, "message": result_message, "event": event}),
                201,
            )
        else:
            return jsonify({"success": False, "message": result_message}), 400

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True, port=5010)
