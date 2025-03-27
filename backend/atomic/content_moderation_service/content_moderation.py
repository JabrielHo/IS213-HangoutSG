from flask import Flask, jsonify
from flask_cors import CORS
import os
from dotenv import load_dotenv
import request
from datetime import datetime
from content_moderation_model import db,ContentModeration
load_dotenv()

app = Flask(__name__)
CORS(app)

app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")

db.init_app(app)


@app.route("/api/moderation/report/post/<string:post_id>", methods=["POST"])
def report_post(post_id):
    try:
        data = request.get_json()

        user_id = data['user_id']
        post_id=data['post_id']
        reason = data.get('reason', 'No reason provided')
        timestamp = datetime.now()
        # save to Database
        flag = ContentModeration(
            post_id=post_id, 
            flagged_by=user_id,
            reason=reason,  
            status="pending",
            created_at=timestamp
        )
        db.session.add(flag)
        db.session.commit()

        
        return jsonify({
            "code": 200,
            "message": "Post successfully reported",
            "flag": flag.json() 
        }), 200
        
    except Exception as e:
        print(f"Exception: {str(e)}")
        return jsonify({
            "code": 500,
            "message": f"An error occurred: {str(e)}"
        }), 500
    

@app.route("/api/moderation/report/comment/<string:comment_id>", methods=["POST"])
def report_comment(comment_id):
    try:
        data = request.get_json()

        user_id = data['user_id']
        comment_id=data['comment_id']
        reason = data.get('reason', 'No reason provided')
        timestamp = datetime.now()
        # save to Database
        flag = ContentModeration(
            comment_id=comment_id, 
            flagged_by=user_id,
            reason=reason,  
            status="pending",
            created_at=timestamp
        )
        db.session.add(flag)
        db.session.commit()

        return jsonify({
            "code": 200,
            "message": "Comment successfully reported",
            "flag": flag.json() 
        }), 200
        
    except Exception as e:
        print(f"Exception: {str(e)}")
        return jsonify({
            "code": 500,
            "message": f"An error occurred: {str(e)}"
        }), 500
    
@app.route("/api/moderation/delete/post/<string:post_id>", methods=["DELETE"])
def delete_post(post_id):
    try:
        #delete from db
        flag = ContentModeration.query.filter_by(post_id=post_id).first()        
        if not flag:
            return jsonify({
                "code": 404,
                "message": f"Post with post_id {post_id} not found."
            }), 404
        db.session.delete(flag)
        db.session.commit()

        return jsonify({
            "code": 200,
            "message": f"Post with post_id {post_id} successfully deleted."
        }), 200
    except Exception as e:
        print(f"Exception: {str(e)}")
        return jsonify({
            "code": 500,
            "message": f"An error occurred: {str(e)}"
        }), 500
    
@app.route("/api/report/delete/comment/<string:comment_id>", methods=["DELETE"])
def delete_comment(comment_id):
    try:
        #delete from db
        flag = ContentModeration.query.filter_by(comment_id=comment_id).first()        
        if not flag:
            return jsonify({
                "code": 404,
                "message": f"Comment with comment_id {comment_id} not found."
            }), 404
        db.session.delete(flag)
        db.session.commit()

        return jsonify({
            "code": 200,
            "message": f"Comment with comment_id {comment_id} successfully deleted."
        }), 200
    except Exception as e:
        print(f"Exception: {str(e)}")
        return jsonify({
            "code": 500,
            "message": f"An error occurred: {str(e)}"
        }), 500



if __name__ == "__main__":
    app.run(port=5000, debug=True)