from flask import Flask, jsonify
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

# ✅ Simulate a message being "consumed" (inserting into database)
@app.route("/mock-messages/<string:user_id>", methods=["POST"])
def mock_messages(user_id):
    sample_message = {
        "receiver_id": "auth0|67cd8623469fee2d24e73bfb",
        "content": "This is a mock message",
        "status": "unread",  # ✅ Always set to "unread" when first created
    }

    new_message = InboxMessage(
        receiver_id=sample_message["receiver_id"],
        content=sample_message["content"],
        status=sample_message["status"],
    )
    db.session.add(new_message)
    db.session.commit()

    # Emit message to frontend via WebSocket
    socketio.emit(
        "new_message",
        {
            "message_id": new_message.message_id,
            "receiver_id": new_message.receiver_id,
            "content": new_message.content,
            "status": new_message.status,
            "created_at": new_message.created_at.isoformat(),
        },
    )

    return jsonify({"message": "Mock message added"}), 201

# ✅ Mark as read (frontend will call this when user opens the message)
@app.route("/mark-as-read/<int:message_id>", methods=["POST"])
def mark_as_read(message_id):
    message = InboxMessage.query.get(message_id)
    if message and message.status != "read":
        message.status = "read"
        db.session.commit()

        # Emit status update to frontend using WebSocket
        socketio.emit(
            "update_message_status",
            {
                "message_id": message.message_id,
                "status": message.status,
            },
        )

        return jsonify({"message": "Message marked as read"}), 200
    return jsonify({"error": "Message not found or already read"}), 404

# ✅ Get messages for a user (fetch inbox from MySQL)
@app.route('/get-messages/<string:user_id>', methods=['GET'])
def get_messages(user_id):
    messages = InboxMessage.query.filter_by(receiver_id=user_id).all()

    if not messages:
        return jsonify([]), 200
    
    return jsonify([
        {
            'message_id': m.message_id,
            'receiver_id': m.receiver_id,
            'content': m.content,
            'status': m.status,
            'created_at': m.created_at.isoformat()
        } for m in messages
    ])

@socketio.on("connect")
def handle_connect():
    print("Client connected")

if __name__ == "__main__":
    socketio.run(app, port=5002)
