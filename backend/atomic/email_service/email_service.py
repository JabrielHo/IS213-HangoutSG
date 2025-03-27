from flask import Flask, jsonify, request
from flask_cors import CORS
from email_model import db, Email
from dotenv import load_dotenv
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
CORS(app)

# Database Config docker
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")

#local 
# app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+mysqlconnector://root:@localhost:3306/email_service"
# app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

# Get SMTP settings from environment variables
SMTP_SERVER = os.getenv("SMTP_SERVER")
SMTP_PORT = os.getenv("SMTP_PORT", 587)  # Default to 587 if not set
SMTP_EMAIL = os.getenv("SMTP_EMAIL")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")

# Function to send email
def send_email_via_smtp(to_email, subject, body):
    try:
        msg = MIMEMultipart()
        msg["From"] = SMTP_EMAIL
        msg["To"] = to_email
        msg["Subject"] = subject

        msg.attach(MIMEText(body, "plain"))

        # Connect to SMTP server
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()  # Secure connection
            server.login(SMTP_EMAIL, SMTP_PASSWORD) 
            server.sendmail(SMTP_EMAIL, to_email, msg.as_string())  

        return True
    except Exception as e:
        print(f"SMTP Error: {e}")
        return False

# CREATE - Send an email
@app.route("/email", methods=["POST"])
def send_email():
    try:
        data = request.get_json()

        # Check for required fields
        required_fields = ["to_email", "subject", "body"]
        missing_fields = [field for field in required_fields if not data.get(field)]

        if missing_fields:
            return jsonify({
                "code": 400,
                "message": f"Invalid input: Missing fields: {', '.join(missing_fields)}."
            }), 400

        # Save to database
        email = Email(
            to_email=data["to_email"],  
            subject=data["subject"],
            body=data["body"]
        )
        db.session.add(email)
        db.session.commit()

        # Send email
        if send_email_via_smtp(data["to_email"], data["subject"], data["body"]):
            return jsonify({
                "code": 201,
                "message": "Email sent successfully",
                "data": email.json()
            }), 201
        else:
            return jsonify({
                "code": 500,
                "message": "Failed to send email"
            }), 500

    except Exception as e:
        db.session.rollback()
        print(f"Exception: {e}")
        return jsonify({
            "code": 500,
            "message": f"An error occurred while sending the email: {e}"
        }), 500

# Uncomment for Docker
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5008)

# Start Flask app locally
# if __name__ == "__main__":
#     app.run(port=5002, debug=True)
