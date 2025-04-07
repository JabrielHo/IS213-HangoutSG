from flask import Flask, jsonify, request
import requests
import os
from dotenv import load_dotenv
from flask_cors import CORS
import pika
import json
import os

load_dotenv()

# Service URLs from environment variables
USER_SERVICE_URL = os.getenv("USER_SERVICE_URL", "http://localhost:5000/api/users")
EMAIL_SERVICE_URL = os.getenv("EMAIL_SERVICE_URL", "http://localhost:5008/api/email")
POST_SERVICE_URL = os.getenv("POST_SERVICE_URL", "http://localhost:5002/api/post")
COMMENT_SERVICE_URL = os.getenv("COMMENT_SERVICE_URL", "http://localhost:5003/api/comment")
CONTENT_MODERATION_URL = os.getenv("CONTENT_MODERATION_URL", "http://localhost:5007/api/moderation")

app = Flask(__name__)
CORS(app)


def publish_to_inbox(message):
    try:
        amqp_host = os.getenv("RABBITMQ_HOST", "localhost")
        amqp_port = int(os.getenv("RABBITMQ_PORT", 5672))
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


def get_user_info(user_id):
    """Fetch user details from the User Service"""
    try:
        response = requests.get(f"{USER_SERVICE_URL}/{user_id}")
        if response.status_code == 200:
            return response.json().get("data")
        return None
    except Exception as e:
        print(f"Error fetching user: {e}")
        return None

def notify_user(email, subject, body):
    """Send an email notification via Email Service"""
    payload = {
        "to_email": email,
        "subject": subject,
        "body": body
    }
    try:
        response = requests.post(EMAIL_SERVICE_URL, json=payload)
        return response.status_code == 201
    except Exception as e:
        print(f"Email notification error: {e}")
        return False

@app.route("/api/ban/content", methods=["POST"])
def ban_content():
    """Ban a post, comment, and notify the user"""
    data = request.get_json()

    flag_id = data.get("flagId")
    
    if not flag_id:
        return jsonify({"code": 400, "message": "Missing flag_id in request body"}), 400

    try:
        response = requests.get(CONTENT_MODERATION_URL+ "/get/"+ flag_id)
        
        if response.status_code != 200:
            return jsonify({"code": 500, "message": "Failed to fetch content details"}), 500
        
        content_details = response.json()
        
        post_id = content_details.get("post_id")
        comment_id = content_details.get("comment_id")
        flagged_by = content_details.get("flagged_by")

        content_type = "post" if post_id else "comment"
        content_id = post_id if post_id else comment_id

        service_url = None
        if content_type == "post":
            service_url = POST_SERVICE_URL+"/"+content_id
            response = requests.get(service_url)
            if response.status_code != 200:
                return jsonify({"code": 500, "message": "Failed to fetch post details"}), 500
            post_data = response.json()
            author_id = post_data.get('data', {}).get('author_id')
        elif content_type == "comment":
            # Send GET request to the COMMENT service
            service_url = COMMENT_SERVICE_URL+"/" +content_id
            response = requests.get(service_url)
            if response.status_code != 200:
                return jsonify({"code": 500, "message": "Failed to fetch comment details"}), 500
            comment_data = response.json()
            author_id = comment_data.get('data', {}).get('author_id')
        else:
            return jsonify({"code": 400, "message": "Invalid content type"}), 400
        
        if service_url:
            update_response = requests.put(service_url+"/status", json={"status": "unpublished"})
            if update_response.status_code != 200:
                return jsonify({"code": 500, "message": "Failed to update content status"}), 500

        # Step 5: Send email notification to the user
        user = get_user_info(author_id)
        
        if not user or not user.get("email"):
            return jsonify({"code": 404, "message": "User not found or email not available"}), 404

        email = user.get("email")
        subject = "Your content has been banned"
        body = f"Dear {user.get('username')},\n\nYour {content_type} with ID {content_id} has been banned due to a policy violation."

        # Send email to the  banned user
        notify_user(email, subject, body)

        #notify flagged by
        publish_to_inbox(
            {
                "type": "report_outcome",
                "receiver_id": flagged_by,
                "subject": "Report Outcome",
                "content": "Your report was successful",
            }
        )

        response = requests.post(f"{USER_SERVICE_URL}/ban/{author_id}",json={"reason": "Inappropriate content reported"})

        # Remove from moderation records
        mod_delete_url = f"{CONTENT_MODERATION_URL}/delete/flag/{flag_id}"
        mod_delete_response = requests.post(mod_delete_url)
        if mod_delete_response.status_code != 200:
            return jsonify({"code": 500, "message": "Failed to delete moderation record"}), 500

        return jsonify({"code": 200, "message": f"{content_type} {content_id} deleted"}), 200
        
        
    except requests.exceptions.RequestException as e:
        # Handle any request exceptions (e.g., server not reachable, timeout, etc.)
        return jsonify({"code": 500, "message": f"Error fetching content details: {str(e)}"}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5011)
