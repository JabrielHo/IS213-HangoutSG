from flask import Flask, jsonify,request
from flask_cors import CORS
import os
from dotenv import load_dotenv
from datetime import datetime
from content_moderation_model import db,ContentModeration
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer

load_dotenv()

app = Flask(__name__)
CORS(app)

app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")

db.init_app(app)


@app.route("/api/moderation/report/post/<string:post_id>", methods=["POST"])
def report_post(post_id):
    try:
        data = request.get_json()
        poster_id = data['poster_id']
        user_id = data['user_id']
        post_id=data['post_id']
        reason = data.get('reason', 'No reason provided')
        timestamp = datetime.now()
        post_content=data['content']

        sia = SentimentIntensityAnalyzer()
        sentiment_score = sia.polarity_scores(post_content)
        if sentiment_score['compound'] <= -0.5: 
            isInappropriate = True  
        isInappropriate = False

        if not isInappropriate:
           return jsonify({
                "code": 200,
                "message": "Post is appropriate and was not flagged"
            }), 200
        # save to Database
        flag = ContentModeration(
            poster_id=poster_id,
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
        poster_id = data['poster_id']
        user_id = data['user_id']
        comment_id=data['comment_id']
        comment_content=data['content']
        reason = data.get('reason', 'No reason provided')
        timestamp = datetime.now()

        sia = SentimentIntensityAnalyzer()
        sentiment_score = sia.polarity_scores(comment_content)
        if sentiment_score['compound'] <= -0.5: 
            isInappropriate = True  
        isInappropriate = False

        if not isInappropriate:
           return jsonify({
                "code": 200,
                "message": "Comment is appropriate and was not flagged"
            }), 200

        # save to Database
        flag = ContentModeration(
            poster_id=poster_id,
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
    
@app.route("/api/moderation/delete/post/<string:post_id>", methods=["POST"]) 
def delete_post(post_id): 
    try: 
        data=request.getjson() 
        post_id=data["post_id"] 
        #delete from db 
        flag = ContentModeration.query.filter_by(post_id=post_id).first()         
        if not flag: 
            return jsonify({ 
                "code": 404, 
                "message": f"Post with post_id {post_id} not found." 
            }), 404 
        flag.isdeleted = True 
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
     
@app.route("/api/moderation/report/delete/comment/<string:comment_id>", methods=["POST"]) 
def delete_comment(comment_id): 
    try: 
        data=request.getjson() 
        comment_id=data["comment_id"] 
        #delete from db 
        flag = ContentModeration.query.filter_by(comment_id=comment_id).first()         
        if not flag: 
            return jsonify({ 
                "code": 404, 
                "message": f"Comment with comment_id {comment_id} not found." 
            }), 404 
        flag.isdeleted = True 
        db.session.commit() 
 
        return jsonify({ 
            "code": 200, 
            "message": f"Comment with comment_id {comment_id} successfully deleted." 
        }), 200 
    except Exception as e: 
        print(f"Exception: {str(e)}") 
        return jsonify({ 
            "code": 500,"message": f"An error occurred: {str(e)}" 
        }), 500 
     
@app.route("/api/moderation/get/", methods=["GET"]) 
def get_all_reported(): 
    try: 
        flagged = ContentModeration.query.filter_by(isdeleted=False).all() 
        if not flagged: 
                return jsonify({ 
                    "code": 404, 
                    "message": "No reported content found." 
                }), 404 
             
        flagged_content_list = [flag.json() for flag in flagged] 
 
        return jsonify({ 
                "code": 200, 
                "message": "Successfully retrieved reported content", 
                "flagged_content": flagged_content_list 
            }), 200 
     
    except Exception as e: 
        print(f"Exception: {str(e)}") 
        return jsonify({ 
            "code": 500, 
            "message": f"An error occurred: {str(e)}" 
        }), 500 


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5007, debug=True)