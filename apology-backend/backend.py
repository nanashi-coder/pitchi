from flask import Flask, request, jsonify
from flask_cors import CORS
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

app = Flask(__name__)
CORS(app)

# Load from environment
EMAIL_ADDRESS = os.environ.get("EMAIL_ADDRESS")
EMAIL_PASSWORD = os.environ.get("EMAIL_PASSWORD")

@app.route("/", methods=["GET"])
def home():
    return "Backend is running!", 200

@app.route("/send-email", methods=["POST"])
def send_email():
    try:
        data = request.get_json()
        recipient = data.get("to")
        subject = data.get("subject")
        message = data.get("message")

        if not recipient or not subject or not message:
            return jsonify({"error": "Missing fields"}), 400

        msg = MIMEMultipart()
        msg["From"] = EMAIL_ADDRESS
        msg["To"] = recipient
        msg["Subject"] = subject
        msg.attach(MIMEText(message, "plain"))

        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        server.sendmail(EMAIL_ADDRESS, recipient, msg.as_string())
        server.quit()

        return jsonify({"success": True, "message": "Email sent!"}), 200

    except Exception as e:
        print("Error sending email:", str(e))  # log to Render console
        return jsonify({"error": str(e)}), 500

@app.route("/send-notification", methods=["POST"])
def send_notification():
    data = request.get_json()
    token = data.get("token")
    title = data.get("title")
    body = data.get("body")

    if not token or not title or not body:
        return jsonify({"error": "Missing fields"}), 400

    print(f"Notification to {token}: {title} - {body}")
    return jsonify({"success": True, "message": "Notification sent (mock)"}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
