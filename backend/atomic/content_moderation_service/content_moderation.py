from flask import Flask, jsonify,request
from flask_cors import CORS
import os
from dotenv import load_dotenv
from datetime import datetime
from content_moderation_model import db,ContentModeration
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
try:
    nltk.data.find('vader_lexicon')
except LookupError:
    nltk.download('vader_lexicon')

load_dotenv()

app = Flask(__name__)
CORS(app)

app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)


@app.route("/api/moderation/report/post/<string:post_id>", methods=["POST"])
def report_post(post_id):
    try:
        data = request.get_json()
        user_id = data['user_id']
        post_id=data['post_id']
        reason = data.get('reason', 'No reason provided')
        post_content=data['content']

        sia = SentimentIntensityAnalyzer()
        sentiment_score = sia.polarity_scores(post_content)
        isInappropriate = False
        if sentiment_score['compound'] <= -0.2: 
            isInappropriate = True  
        

        if not isInappropriate:
           print(sentiment_score['compound'])
           return jsonify({
                "code": 201,
                "message": "Post is appropriate and was not flagged"
            }), 201
        # save to Database
        flag = ContentModeration(
            post_id=post_id, 
            flagged_by=user_id,
            reason=reason,  
            status="pending"
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
        comment_content=data['content']
        reason = data.get('reason', 'No reason provided')

        sia = SentimentIntensityAnalyzer()
        sentiment_score = sia.polarity_scores(comment_content)
        isInappropriate = False
        if sentiment_score['compound'] <= -0.2: 
            isInappropriate = True  
        

        if not isInappropriate:
           print(sentiment_score['compound'])
           return jsonify({
                "code": 201,
                "message": "Comment is appropriate and was not flagged"
            }), 201

        # save to Database
        flag = ContentModeration(
            comment_id=comment_id, 
            flagged_by=user_id,
            reason=reason,  
            status="pending"
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

@app.route("/api/moderation/delete/flag/<string:flag_id>", methods=["POST"]) 
def delete_flag(flag_id): 
    try: 
        
        flag = ContentModeration.query.filter_by(flag_id=flag_id).first()         
        if not flag: 
            return jsonify({ 
                "code": 404, 
                "message": f"Flag with flag_id {flag_id} not found." 
            }), 404 
        flag.isdeleted = True 
        db.session.commit() 
 
        return jsonify({ 
            "code": 200, 
            "message": f"Flag with flag_id {flag_id} successfully deleted." 
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

@app.route("/api/moderation/get/<string:flag_id>", methods=["GET"]) 
def get_reported_by_flag_id(flag_id): 
    try: 
        # Filter content by the provided flag_id
        flagged = ContentModeration.query.filter_by(flag_id=flag_id, isdeleted=False).all()
        
        if not flagged:
            return jsonify({ 
                "code": 404, 
                "message": "No reported content found for the provided flag_id." 
            }), 404 
        flag = flagged[0]
        
        post_id=flag.post_id
        comment_id = flag.comment_id
        flagged_by = flag.flagged_by


        return jsonify({ 
            "code": 200, 
            "message": "Successfully retrieved reported content", 
            "post_id": post_id,
            "comment_id": comment_id,
            "flagged_by": flagged_by
        }), 200 
     
    except Exception as e: 
        print(f"Exception: {str(e)}") 
        return jsonify({ 
            "code": 500, 
            "message": f"An error occurred: {str(e)}" 
        }), 500


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5007)