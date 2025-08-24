from flask import Flask, request, jsonify
import smtplib, ssl
from email.mime.text import MIMEText
from datetime import datetime
import os

app = Flask(__name__)

# Gmail settings
SENDER_EMAIL   = os.environ.get("SENDER_EMAIL")   # set in Render dashboard
APP_PASSWORD   = os.environ.get("APP_PASSWORD")   # set in Render dashboard
RECEIVER_EMAIL = os.environ.get("RECEIVER_EMAIL") # your personal email

@app.route("/send-notification", methods=["POST"])
def send_notification():
    try:
        data = request.get_json()
        name = data.get("name", "")
        action = data.get("action", "")

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Email content
        text = f"Name: {name}\nAction: {action}\nTime: {timestamp}"
        msg = MIMEText(text, "plain")
        msg["Subject"] = "Forgiveness App Response"
        msg["From"] = SENDER_EMAIL
        msg["To"] = RECEIVER_EMAIL

        # Send email
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
            server.login(SENDER_EMAIL, APP_PASSWORD)
            server.sendmail(SENDER_EMAIL, RECEIVER_EMAIL, msg.as_string())

        return jsonify({"success": True, "message": "Notification sent!"}), 200

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
