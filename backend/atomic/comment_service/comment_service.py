from flask import Flask, jsonify, request
from flask_cors import CORS
from comment_model import db, Comment
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)
CORS(app)

app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

# CREATE - Create a new comment
@app.route("/api/comment", methods=["POST"])
def create_comment():
    try:
        data = request.get_json()
        required_fields = ["post_id", "author_id", "content", "parent_id"]
        missing = [f for f in required_fields if not data.get(f)]

        if missing:
            return jsonify({
                "code": 400,
                "message": f"Missing fields: {', '.join(missing)}"
            }), 400

        comment = Comment(
            post_id=data["post_id"],
            author_id=data["author_id"],
            content=data["content"],
            parent_id=data["parent_id"]
        )

        db.session.add(comment)
        db.session.commit()

        return jsonify({
            "code": 201,
            "message": "Comment created successfully",
            "data": comment.json()
        }), 201

    except Exception as e:
        db.session.rollback()
        print(f"Error: {e}")
        return jsonify({
            "code": 500,
            "message": f"Error creating comment: {e}"
        }), 500

# READ - Get all comments
@app.route("/api/comments", methods=["GET"])
def get_all_comments():
    try:
        comments = Comment.query.all()
        return jsonify({
            "code": 200,
            "data": {"comments": [c.json() for c in comments]}
        }), 200
    except Exception as e:
        return jsonify({
            "code": 500,
            "message": f"Error retrieving comments: {e}"
        }), 500

# READ - Get comments by post_id
@app.route("/api/comments/post/<string:post_id>", methods=["GET"])
def get_comments_by_post(post_id):
    try:
        comments = Comment.query.filter_by(post_id=post_id).all()
        return jsonify({
            "code": 200,
            "data": {"comments": [c.json() for c in comments]}
        }), 200
    except Exception as e:
        return jsonify({
            "code": 500,
            "message": f"Error retrieving comments: {e}"
        }), 500

# READ - Get comments by author
@app.route("/api/comments/author/<string:author_id>", methods=["GET"])
def get_comments_by_author(author_id):
    try:
        comments = Comment.query.filter_by(author_id=author_id).all()
        return jsonify({
            "code": 200,
            "data": {"comments": [c.json() for c in comments]}
        }), 200
    except Exception as e:
        return jsonify({
            "code": 500,
            "message": f"Error retrieving comments: {e}"
        }), 500
    

# READ - Get a specific comment by comment_id
@app.route("/api/comment/<string:comment_id>", methods=["GET"])
def get_comment_by_id(comment_id):
    try:
        comment = Comment.query.get(comment_id)
        if comment:
            return jsonify({
                "code": 200,
                "data": comment.json()
            }), 200
        else:
            return jsonify({
                "code": 404,
                "message": f"Comment not found with ID: {comment_id}"
            }), 404
    except Exception as e:
        return jsonify({
            "code": 500,
            "message": f"Error retrieving comment: {e}"
        }), 500
    
# UPDATE - Change comment status (published/unpublished)
@app.route("/api/comment/<string:comment_id>/status", methods=["PUT"])
def update_comment_status(comment_id):
    try:
        data = request.get_json()
        new_status = data.get("status")

        if new_status not in ["published", "unpublished"]:
            return jsonify({
                "code": 400,
                "message": "Invalid status. Use 'published' or 'unpublished'."
            }), 400

        comment = Comment.query.get(comment_id)
        if not comment:
            return jsonify({"code": 404, "message": "Comment not found"}), 404

        comment.status = new_status
        db.session.commit()

        return jsonify({
            "code": 200,
            "message": "Comment status updated",
            "data": comment.json()
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({
            "code": 500,
            "message": f"Error updating comment: {e}"
        }), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5003)
