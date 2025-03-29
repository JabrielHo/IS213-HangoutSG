from flask import Flask, jsonify
from inbox_model import db, InboxMessage
from flask_socketio import SocketIO
import os
import threading
import sys
from dotenv import load_dotenv
from flask_cors import CORS

sys.path.append("../../rabbitmq")
from consumer import MessageConsumer

load_dotenv()

app = Flask(__name__)
CORS(app)

app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
socketio = SocketIO(app, cors_allowed_origins="*")

db.init_app(app)

def start_consumer():
    consumer = MessageConsumer("inbox_messages", handle_inbox_message)
    consumer.start_consuming()


# Message handler for RabbitMQ consumer
def handle_inbox_message(message, routing_key):
    """
    Process messages from the inbox queue with support for different message types:
    
    - Single recipient messages: { "type": "report_outcome", "receiver_id": "userId", "subject": "...", "content": "..." }
    - Multi-recipient messages: { "type": "event_creation", "receiver_ids": ["userId1", "userId2"], "subject": "...", "content": "..." }
    
    Args:
        message: The message payload from RabbitMQ
        routing_key: The routing key used for the message
    """
    print(f"Processing inbox message: {message}")
    
    # Validate basic message structure
    if "type" not in message:
        print("Error: Message missing 'type' field")
        return
        
    message_type = message.get("type")
    
    # Process based on message type
    if message_type == "event_creation":
        # Multi-recipient message
        if "receiver_ids" not in message or "subject" not in message or "content" not in message:
            print(f"Error: Missing required fields for event_creation message: {message}")
            return
            
        receiver_ids = message["receiver_ids"]
        subject = message["subject"]
        content = message["content"]
        
        # Send to each recipient
        for receiver_id in receiver_ids:
            _create_inbox_message(receiver_id, subject, content)
            
    elif message_type == "report_outcome":
        # Single recipient message
        if "receiver_id" not in message or "subject" not in message or "content" not in message:
            print(f"Error: Missing required fields for {message_type} message: {message}")
            return
            
        receiver_id = message["receiver_id"]
        subject = message["subject"]
        content = message["content"]
        
        _create_inbox_message(receiver_id, subject, content)
        
    else:
        print(f"Warning: Unknown message type '{message_type}'")


def _create_inbox_message(receiver_id, subject, content):
    with app.app_context():
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
        except Exception as e:
            print(f"Error processing message: {str(e)}")
            db.session.rollback()

# Mark as read
@app.route("/api/inbox/read/<string:message_id>", methods=["POST"])
def mark_as_read(message_id):
    message = InboxMessage.query.get(message_id)
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


# Get messages for a user
@app.route("/api/inbox/<string:user_id>", methods=["GET"])
def get_messages(user_id):
    try:
        messages = InboxMessage.query.filter_by(receiver_id=user_id).all()
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
    # Start consumer in a separate thread
    consumer_thread = threading.Thread(target=start_consumer, daemon=True)
    consumer_thread.start()

    # Uncomment for docker
    # socketio.run(app, host="0.0.0.0", port=5006, allow_unsafe_werkzeug=True)

    # Uncomment for local
    socketio.run(app, port=5006, allow_unsafe_werkzeug=True)
