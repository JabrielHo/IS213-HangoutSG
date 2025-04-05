from flask import Flask, jsonify, request
from flask_cors import CORS
from community_model import db, Community
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)
CORS(app)

app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

# CREATE - Create a new community
@app.route("/api/community", methods=["POST"])
def create_community():
    try:
        data = request.get_json()
        
        # Check for required fields and empty values
        required_fields = ["name", "description", "creator_id"]
        missing_fields = []
        
        for field in required_fields:
            if field not in data:
                missing_fields.append(field)
            elif not data[field] or data[field].strip() == "":
                missing_fields.append(field)
        
        if missing_fields:
            return jsonify({
                "code": 400,
                "message": f"Invalid input: Required fields are missing or empty: {', '.join(missing_fields)}."
            }), 400
        
        # Check if a community with this name already exists
        existing_community = Community.query.filter_by(name=data["name"]).first()
        if existing_community:
            return jsonify({
                "code": 409,
                "message": f"A community with the name '{data['name']}' already exists."
            }), 409
            
        community = Community(
            name=data["name"].lower(),
            description=data["description"],
            creator_id=data["creator_id"]
        )
        
        db.session.add(community)
        db.session.commit()
        
        return jsonify({
            "code": 201,
            "message": "Community created successfully",
            "data": community.json()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        # Log the actual error for debugging
        print(f"Exception: {str(e)}")
        return jsonify({
            "code": 500,
            "message": f"An error occurred while creating the community: {str(e)}"
        }), 500

# READ - Get all communities
@app.route("/api/community", methods=["GET"])
def get_all_communities():
    try:
        communities = Community.query.all()
        return jsonify({
            "code": 200,
            "data": {
                "communities": [community.json() for community in communities]
            }
        })
        
    except Exception as e:
        return jsonify({
            "code": 500,
            "message": f"An error occurred while retrieving communities: {str(e)}"
        }), 500

# READ - Get a specific community by ID
@app.route("/api/community/<string:community_id>", methods=["GET"])
def get_community(community_id):
    try:
        community = Community.query.get(community_id)
        if community:
            return jsonify({
                "code": 200,
                "data": community.json()
            })
        return jsonify({
            "code": 404,
            "message": f"Community not found with ID: {community_id}"
        }), 404
        
    except Exception as e:
        return jsonify({
            "code": 500,
            "message": f"An error occurred while retrieving the community: {str(e)}"
        }), 500
    
# READ - Get a specific community by name
@app.route("/api/community/name/<string:community_name>", methods=["GET"])
def get_community_by_name(community_name):
    try:
        community = Community.query.filter_by(name=community_name.lower()).first()
        if community:
            return jsonify({
                "code": 200,
                "data": community.json()
            })
        return jsonify({
            "code": 404,
            "message": f"Community not found with name: {community_name}"
        }), 404
        
    except Exception as e:
        return jsonify({
            "code": 500,
            "message": f"An error occurred while retrieving the community: {str(e)}"
        }), 500

# READ - Get communities by creator ID
@app.route("/api/community/creator/<string:creator_id>", methods=["GET"])
def get_communities_by_creator(creator_id):
    try:
        communities = Community.query.filter_by(creator_id=creator_id).all()
        return jsonify({
            "code": 200,
            "data": {
                "communities": [community.json() for community in communities]
            }
        })
        
    except Exception as e:
        return jsonify({
            "code": 500,
            "message": f"An error occurred while retrieving communities: {str(e)}"
        }), 500

if __name__ == "__main__":
    # Uncomment for docker
    app.run(host="0.0.0.0", port=5001)
    app.run(port=5001, debug=True)