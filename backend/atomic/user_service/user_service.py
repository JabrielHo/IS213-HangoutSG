from flask import Flask, jsonify, request
from flask_cors import CORS
import os
from dotenv import load_dotenv
import requests
import datetime

load_dotenv()

AUTH0_DOMAIN = os.getenv("AUTH0_DOMAIN")
AUTH0_CLIENT_ID = os.getenv("AUTH0_CLIENT_ID")
AUTH0_CLIENT_SECRET = os.getenv("AUTH0_CLIENT_SECRET")

app = Flask(__name__)
CORS(app)

def get_management_api_token():
    """Get Auth0 Management API token"""
    url = f"https://{AUTH0_DOMAIN}/oauth/token"
    payload = {
        "client_id": AUTH0_CLIENT_ID,
        "client_secret": AUTH0_CLIENT_SECRET,
        "audience": f"https://{AUTH0_DOMAIN}/api/v2/",
        "grant_type": "client_credentials"
    }
    headers = {"content-type": "application/json"}
    
    response = requests.post(url, json=payload, headers=headers)
    if response.status_code != 200:
        print(f"Token error: {response.status_code} - {response.text}")
        raise Exception(f"Failed to get token: {response.text}")
    
    data = response.json()
    return data["access_token"]

@app.route("/api/users/<string:user_id>", methods=["GET"])
def get_user(user_id):
    try:
        # Get management API token
        token = get_management_api_token()
        
        # Make direct API call to Auth0 Management API
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        url = f"https://{AUTH0_DOMAIN}/api/v2/users/{user_id}"
        
        response = requests.get(url, headers=headers)
        
        if response.status_code != 200:
            print(f"User fetch error: {response.status_code} - {response.text}")
            return jsonify({
                "code": response.status_code, 
                "message": f"Auth0 error: {response.text}"
            }), response.status_code
        
        user = response.json()
        return jsonify({"code": 200, "data": user}), 200
    except Exception as e:
        print(f"Exception: {str(e)}")
        return jsonify({"code": 500, "message": f"An error occurred: {str(e)}"}), 500
    
@app.route("/api/users/ban/<string:user_id>", methods=["POST"])
def ban_user(user_id):
    try:
        # Get management API token
        token = get_management_api_token()
        
        # Get ban reason from request body
        request_data = request.get_json()
        ban_reason = request_data.get('reason', 'Violation of terms of service')
        
        # Prepare user data to update
        user_data = {
            "blocked": True,
            "user_metadata": {
                "ban_info": {
                    "reason": ban_reason,
                    "date": datetime.datetime.now().isoformat()
                }
            }
        }
        
        # Make API call to Auth0 Management API to update user
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        url = f"https://{AUTH0_DOMAIN}/api/v2/users/{user_id}"
        
        response = requests.patch(url, json=user_data, headers=headers)
        
        if response.status_code != 200:
            print(f"User ban error: {response.status_code} - {response.text}")
            return jsonify({
                "code": response.status_code, 
                "message": f"Auth0 error: {response.text}"
            }), response.status_code
        
        return jsonify({
            "code": 200, 
            "message": f"User {user_id} has been banned",
            "data": response.json()
        }), 200
    except Exception as e:
        print(f"Exception in ban_user: {str(e)}")
        return jsonify({"code": 500, "message": f"An error occurred: {str(e)}"}), 500

if __name__ == "__main__":
    app.run(port=5000, debug=True)