from flask import Flask, request, jsonify
from flask_cors import CORS
from post_model import db, Post
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)
CORS(app)

# Docker
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")

# Local
# app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+mysqlconnector://root:is213@localhost:3306/post_service"
# app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

# CREATE - Create a new post
@app.route("/api/post", methods=["POST"])
def create_post():
    try:
        data = request.get_json()

        required_fields = ["community_id", "author_id", "title", "content"]
        missing = [field for field in required_fields if not data.get(field)]
        if missing:
            return jsonify({"code": 400, "message": f"Missing fields: {', '.join(missing)}"}), 400

        post = Post(
            community_id=data["community_id"],
            author_id=data["author_id"],
            title=data["title"],
            content=data["content"]
        )
        db.session.add(post)
        db.session.commit()

        return jsonify({"code": 201, "message": "Post created", "data": post.json()}), 201

    except Exception as e:
        db.session.rollback()
        print(f"Error: {e}")
        return jsonify({"code": 500, "message": f"Error creating post: {e}"}), 500

# READ - Get all posts
@app.route("/api/posts", methods=["GET"])
def get_all_posts():
    try:
        posts = Post.query.all()
        return jsonify({
            "code": 200,
            "data": {"posts": [p.json() for p in posts]}
        }), 200
    except Exception as e:
        return jsonify({"code": 500, "message": f"Error retrieving posts: {e}"}), 500

# READ - Get posts in a specific community
@app.route("/api/posts/community/<string:community_id>", methods=["GET"])
def get_posts_by_community(community_id):
    try:
        posts = Post.query.filter_by(community_id=community_id).all()
        return jsonify({
            "code": 200,
            "data": {"posts": [p.json() for p in posts]}
        }), 200
    except Exception as e:
        return jsonify({"code": 500, "message": f"Error retrieving posts: {e}"}), 500

# READ - Get posts by a specific user
@app.route("/api/posts/author/<string:author_id>", methods=["GET"])
def get_posts_by_author(author_id):
    try:
        posts = Post.query.filter_by(author_id=author_id).all()
        return jsonify({
            "code": 200,
            "data": {"posts": [p.json() for p in posts]}
        }), 200
    except Exception as e:
        return jsonify({"code": 500, "message": f"Error retrieving posts: {e}"}), 500
    
# READ - Get a specific post by post_id
@app.route("/api/post/<string:post_id>", methods=["GET"])
def get_post_by_id(post_id):
    try:
        post = Post.query.get(post_id)
        if post:
            return jsonify({
                "code": 200,
                "data": post.json()
            }), 200
        else:
            return jsonify({
                "code": 404,
                "message": f"Post not found with ID: {post_id}"
            }), 404
    except Exception as e:
        return jsonify({
            "code": 500,
            "message": f"Error retrieving post: {e}"
        }), 500


# UPDATE - Change post status (published/unpublished)
@app.route("/api/post/<string:post_id>/status", methods=["PUT"])
def update_post_status(post_id):
    try:
        data = request.get_json()
        new_status = data.get("status")

        if new_status not in ["published", "unpublished"]:
            return jsonify({"code": 400, "message": "Invalid status. Use 'published' or 'unpublished'."}), 400

        post = Post.query.get(post_id)
        if not post:
            return jsonify({"code": 404, "message": "Post not found"}), 404

        post.status = new_status
        db.session.commit()

        return jsonify({"code": 200, "message": "Post status updated", "data": post.json()}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"code": 500, "message": f"Error updating post status: {e}"}), 500

# Run App
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5002)
