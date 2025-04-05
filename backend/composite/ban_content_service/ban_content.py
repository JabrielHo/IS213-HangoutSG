from flask import Flask, jsonify, request
import requests
import os
from dotenv import load_dotenv

load_dotenv()

# Service URLs from environment variables
USER_SERVICE_URL = os.getenv("USER_SERVICE_URL", "http://localhost:5000/api/users")
EMAIL_SERVICE_URL = os.getenv("EMAIL_SERVICE_URL", "http://localhost:5008/api/email")
POST_SERVICE_URL = os.getenv("POST_SERVICE_URL", "http://localhost:5003/api/post")
COMMENT_SERVICE_URL = os.getenv("COMMENT_SERVICE_URL", "http://localhost:5004/api/comment")
CONTENT_MODERATION_URL = os.getenv("CONTENT_MODERATION_URL", "http://localhost:5007/api/moderation")
INBOX_SERVICE_URL = os.getenv("INBOX_SERVICE_URL", "http://localhost:5002") # <--idk about this

app = Flask(__name__)

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
    """Ban a post, comment, or user and notify them"""
    data = request.get_json()
    user_id = data.get("user_id")
    content_id = data.get("content_id")
    content_type = data.get("content_type")  # "post" or "comment"

    if not user_id or not content_id or not content_type:
        return jsonify({"code": 400, "message": "Missing required fields"}), 400

    # Get user details
    user = get_user_info(user_id)
    if not user:
        return jsonify({"code": 404, "message": "User not found"}), 404
    
    email = user.get("email")
    if not email:
        return jsonify({"code": 400, "message": "User email not found"}), 400

    # Update content status to "unpublished"
    service_url = None
    if content_type == "post":
        service_url = f"{POST_SERVICE_URL}/{content_id}/status"
    elif content_type == "comment":
        service_url = f"{COMMENT_SERVICE_URL}/{content_id}/status"
    
    if service_url:
        update_response = requests.put(service_url, json={"status": "unpublished"})
        if update_response.status_code != 200:
            return jsonify({"code": 500, "message": "Failed to update content status"}), 500

    # Send email notification
    subject = "Your content has been banned"
    body = f"Dear {user.get('username')},\n\nYour {content_type} with ID {content_id} has been banned due to a policy violation."

    if notify_user(email, subject, body):
        return jsonify({"code": 200, "message": f"{content_type} banned and user notified"}), 200
    else:
        return jsonify({"code": 500, "message": "Failed to notify user"}), 500

@app.route("/api/delete/<string:content_type>/<string:content_id>", methods=["DELETE"])
def delete_content(content_type, content_id):
    """Delete a post or comment and remove its record from the moderation system"""
    if content_type not in ["post", "comment"]:
        return jsonify({"code": 400, "message": "Invalid content type"}), 400

    # Call respective service for deletion
    service_url = f"{POST_SERVICE_URL}/delete/{content_id}" if content_type == "post" else f"{COMMENT_SERVICE_URL}/delete/{content_id}"
    
    delete_response = requests.delete(service_url)
    if delete_response.status_code != 200:
        return jsonify({"code": 500, "message": "Failed to delete content"}), 500

    # Remove from moderation records
    mod_delete_url = f"{CONTENT_MODERATION_URL}/delete/{content_type}/{content_id}"
    mod_delete_response = requests.post(mod_delete_url)

    if mod_delete_response.status_code != 200:
        return jsonify({"code": 500, "message": "Failed to delete moderation record"}), 500

    return jsonify({"code": 200, "message": f"{content_type} {content_id} deleted"}), 200

def notify_reporter(reporting_user_id, content_id, content_type):
    """Notify the user who reported the content that it has been banned."""
    try:
        # Compose the message content
        message_content = f"Your report for the {content_type} with ID {content_id} has been successfully processed and banned."
        
        # Send the notification message to the reporting user
        response = requests.post(f"{INBOX_SERVICE_URL}/mock-messages/{reporting_user_id}", json={
            "content": message_content,
            "receiver_id": reporting_user_id,
            "status": "unread"
        })
        
        if response.status_code == 201:
            print(f"Successfully notified the reporter (User ID: {reporting_user_id})")
        else:
            print(f"Failed to notify reporter: {response.status_code}, {response.text}")
    except Exception as e:
        print(f"Error notifying reporter: {e}")

# @app.route("/api/ban/reported", methods=["POST"])
# def ban_reported_content():
#     """Fetch flagged posts and comments from moderation and unpublish them"""
#     try:
#         response = requests.get(f"{CONTENT_MODERATION_URL}/get/")
#         if response.status_code != 200:
#             return jsonify({"code": response.status_code, "message": "Failed to fetch reports"}), response.status_code

#         reported_content = response.json().get("flagged_content", [])
#         if not reported_content:
#             return jsonify({"code": 404, "message": "No reported content found"}), 404

#         updated_content = []
#         for content in reported_content:
#             content_type = "post" if "post_id" in content else "comment"
#             content_id = content.get("post_id") or content.get("comment_id")
            
#             if content_id:
#                 # Unpublish the reported content (ban it)
#                 update_response = requests.put(
#                     f"{POST_SERVICE_URL if content_type == 'post' else COMMENT_SERVICE_URL}/{content_id}/status",
#                     json={"status": "unpublished"}
#                 )
#                 if update_response.status_code == 200:
#                     updated_content.append(content_id)
                    
#                     # Notify the reporter that their report was successful
#                     reporting_user_id = content.get("reporting_user_id")  # Assumes the reported content includes a reporting user ID
#                     if reporting_user_id:
#                         notify_reporter(reporting_user_id, content_id, content_type)

#         return jsonify({
#             "code": 200,
#             "message": "Reported content unpublished",
#             "updated_content": updated_content
#         }), 200

#     except Exception as e:
#         return jsonify({"code": 500, "message": f"Error: {e}"}), 500

if __name__ == "__main__":
    app.run(port=5011, debug=True)
