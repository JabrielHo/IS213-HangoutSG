from flask import Flask, request, jsonify
from inbox_model import db, InboxMessage
from flask_socketio import SocketIO
import os
from dotenv import load_dotenv
from flask_cors import CORS

load_dotenv()

app = Flask(__name__)
CORS(app)

app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
socketio = SocketIO(app, cors_allowed_origins="*")

db.init_app(app)

def insert_into_db(receiver_id, subject, content):
    try:
        new_message = InboxMessage(
            receiver_id=receiver_id,
            subject=subject,
            content=content,
            status="unread",
        )
        db.session.add(new_message)
        db.session.commit()

        socketio.emit(
            "new_message",
            {
                "message_id": new_message.message_id,
                "receiver_id": new_message.receiver_id,
                "subject": new_message.subject,
                "content": new_message.content,
                "status": new_message.status,
                "created_at": new_message.created_at.isoformat(),
            },
        )
        print(f"Message stored and emitted: {new_message.message_id}")
        return new_message
    except Exception as e:
        print(f"Error processing message: {str(e)}")
        db.session.rollback()
        return None

# New endpoint to create inbox messages
@app.route("/api/inbox/create", methods=["POST"])
def create_inbox_message():
    data = request.get_json()
    
    # Validate message type
    if "type" not in data:
        return jsonify({"error": "Message missing 'type' field"}), 400
        
    message_type = data.get("type")
    
    # Process based on message type
    if message_type == "event_creation":
        # Multi-recipient message
        if "receiver_ids" not in data or "subject" not in data or "content" not in data:
            return jsonify({"error": "Missing required fields for event_creation message"}), 400
            
        receiver_ids = data["receiver_ids"]
        subject = data["subject"]
        content = data["content"]
        
        # Send to each recipient
        created_messages = []
        for receiver_id in receiver_ids:
            message = insert_into_db(receiver_id, subject, content)
            if message:
                created_messages.append(message.message_id)
                
        return jsonify({
            "message": f"Created {len(created_messages)} messages successfully", 
            "message_ids": created_messages
        }), 201
            
    elif message_type == "report_outcome" or message_type == "event_registration_outcome":
        # Single recipient message
        if "receiver_id" not in data or "subject" not in data or "content" not in data:
            return jsonify({"error": f"Missing required fields for {message_type} message"}), 400
            
        receiver_id = data["receiver_id"]
        subject = data["subject"]
        content = data["content"]
        
        message = insert_into_db(receiver_id, subject, content)
        if message:
            return jsonify({
                "message": "Message created successfully", 
                "message_id": message.message_id
            }), 201
        else:
            return jsonify({"error": "Failed to create message"}), 500
        
    else:
        return jsonify({"error": f"Unknown message type '{message_type}'"}), 400

# Mark as read
@app.route("/api/inbox/read/<string:message_id>", methods=["POST"])
def mark_as_read(message_id):
    message = db.session.get(InboxMessage, message_id)
    if message and message.status != "read":
        message.status = "read"
        db.session.commit()

        socketio.emit(
            "update_message_status",
            {
                "message_id": message.message_id,
                "status": message.status,
            },
        )

        return jsonify({"message": "Message marked as read"}), 200
    return jsonify({"error": "Message not found or already read"}), 404

# Soft delete a message
@app.route("/api/inbox/delete/<string:message_id>", methods=["POST"])
def soft_delete_message(message_id):
    message = db.session.get(InboxMessage, message_id)
    if not message:
        return jsonify({"error": "Message not found"}), 404
        
    if message.status == "deleted":
        return jsonify({"error": "Message already deleted"}), 400
        
    # Perform soft delete by updating status
    message.status = "deleted"
    db.session.commit()
    
    # Notify clients through WebSocket
    socketio.emit(
        "update_message_status",
        {
            "message_id": message.message_id,
            "status": message.status,
        },
    )
    
    return jsonify({"message": "Message deleted successfully"}), 200

# Get messages for a user
@app.route("/api/inbox/<string:user_id>", methods=["GET"])
def get_messages(user_id):
    try:
        messages = InboxMessage.query.filter_by(receiver_id=user_id).filter(InboxMessage.status != "deleted").all()
        return jsonify(
            [
                {
                    "message_id": m.message_id,
                    "receiver_id": m.receiver_id,
                    "subject": m.subject,
                    "content": m.content,
                    "status": m.status,
                    "created_at": m.created_at.isoformat(),
                }
                for m in messages
            ]
        )
    except Exception as e:
        print(f"Error retrieving messages for user {user_id}: {str(e)}")
        return jsonify({"error": "Failed to retrieve messages"}), 500


@socketio.on("connect")
def handle_connect():
    print("Client connected")

if __name__ == "__main__":
    # Uncomment for docker
    # socketio.run(app, host="0.0.0.0", port=5006, allow_unsafe_werkzeug=True)

    # Uncomment for local
    socketio.run(app, port=5006, allow_unsafe_werkzeug=True)