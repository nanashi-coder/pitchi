from flask import Flask, request, jsonify
from flask_cors import CORS
import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import os

app = Flask(__name__)
CORS(app)  # Allow requests from Flutter app

# Email configuration
SENDER_EMAIL = os.environ.get('SENDER_EMAIL', "toqitamimprotik@gmail.com")
APP_PASSWORD = os.environ.get('APP_PASSWORD', "vjakoxonkqweqqqt")
RECEIVER_EMAIL = os.environ.get('RECEIVER_EMAIL', "toqitamimprotik@gmail.com")

def send_email(subject, body):
    """Send email notification"""
    try:
        msg = MIMEMultipart()
        msg['From'] = SENDER_EMAIL
        msg['To'] = RECEIVER_EMAIL
        msg['Subject'] = subject
        
        msg.attach(MIMEText(body, 'plain'))
        
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
            server.login(SENDER_EMAIL, APP_PASSWORD)
            server.sendmail(SENDER_EMAIL, RECEIVER_EMAIL, msg.as_string())
        
        return True
    except Exception as e:
        print(f"Email error: {e}")
        return False

@app.route('/send-notification', methods=['POST'])
def send_notification():
    """Endpoint for Flutter app to send email notifications"""
    try:
        data = request.get_json()
        name = data.get('name', 'Unknown')
        action = data.get('action', 'Unknown action')
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Create email content
        subject = f"Apology App - {action}"
        body = f"Name: {name}\nAction: {action}\nTimestamp: {timestamp}"
        
        # Send email
        success = send_email(subject, body)
        
        if success:
            return jsonify({'status': 'success', 'message': 'Email sent successfully'})
        else:
            return jsonify({'status': 'error', 'message': 'Failed to send email'}), 500
            
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'message': 'Backend is running'})

@app.route('/', methods=['GET'])
def home():
    """Home page"""
    return """
    <h1>Apology App Backend</h1>
    <p>Backend is running successfully!</p>
    <p>Endpoints:</p>
    <ul>
        <li>POST /send-notification - Send email notifications</li>
        <li>GET /health - Health check</li>
    </ul>
    """

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
