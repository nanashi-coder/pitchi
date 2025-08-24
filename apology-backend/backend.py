from flask import Flask, request, jsonify
from flask_cors import CORS
import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# CORS configuration - more specific for production
if os.environ.get('FLASK_ENV') == 'production':
    # In production, specify allowed origins
    CORS(app, origins=[
        "http://localhost:3000",  # For local testing
        "https://your-frontend-domain.com"  # Replace with your actual frontend domain
    ])
else:
    # In development, allow all origins
    CORS(app)

# Email configuration with validation
SENDER_EMAIL = os.environ.get('SENDER_EMAIL')
APP_PASSWORD = os.environ.get('APP_PASSWORD')
RECEIVER_EMAIL = os.environ.get('RECEIVER_EMAIL')

# Validate required environment variables
if not all([SENDER_EMAIL, APP_PASSWORD, RECEIVER_EMAIL]):
    logger.error("Missing required environment variables: SENDER_EMAIL, APP_PASSWORD, or RECEIVER_EMAIL")
    raise ValueError("Email configuration incomplete")

def send_email(subject, body):
    """Send email notification with improved error handling"""
    try:
        logger.info(f"Attempting to send email: {subject}")
        
        msg = MIMEMultipart()
        msg['From'] = SENDER_EMAIL
        msg['To'] = RECEIVER_EMAIL
        msg['Subject'] = subject
        
        msg.attach(MIMEText(body, 'plain'))
        
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
            server.login(SENDER_EMAIL, APP_PASSWORD)
            server.sendmail(SENDER_EMAIL, RECEIVER_EMAIL, msg.as_string())
        
        logger.info("Email sent successfully")
        return True
        
    except smtplib.SMTPAuthenticationError as e:
        logger.error(f"SMTP Authentication error: {e}")
        return False
    except smtplib.SMTPException as e:
        logger.error(f"SMTP error: {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected email error: {e}")
        return False

@app.route('/send-notification', methods=['POST'])
def send_notification():
    """Endpoint for Flutter app to send email notifications"""
    try:
        # Validate request content type
        if not request.is_json:
            return jsonify({
                'status': 'error', 
                'message': 'Content-Type must be application/json'
            }), 400
        
        data = request.get_json()
        
        # Validate required fields
        if not data:
            return jsonify({
                'status': 'error', 
                'message': 'No data provided'
            }), 400
        
        name = data.get('name', 'Unknown')
        action = data.get('action', 'Unknown action')
        
        # Validate that required fields are not empty
        if not name.strip() or not action.strip():
            return jsonify({
                'status': 'error', 
                'message': 'Name and action are required fields'
            }), 400
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Create email content
        subject = f"Apology App - {action}"
        body = f"""
Apology App Notification

Name: {name}
Action: {action}
Timestamp: {timestamp}

This notification was sent from the Apology App.
        """.strip()
        
        # Send email
        success = send_email(subject, body)
        
        if success:
            logger.info(f"Notification sent for user: {name}, action: {action}")
            return jsonify({
                'status': 'success', 
                'message': 'Email sent successfully',
                'timestamp': timestamp
            })
        else:
            logger.error(f"Failed to send notification for user: {name}")
            return jsonify({
                'status': 'error', 
                'message': 'Failed to send email notification'
            }), 500
            
    except Exception as e:
        logger.error(f"Unexpected error in send_notification: {e}")
        return jsonify({
            'status': 'error', 
            'message': 'Internal server error'
        }), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint for Render"""
    try:
        # Test email configuration
        email_config_valid = all([SENDER_EMAIL, APP_PASSWORD, RECEIVER_EMAIL])
        
        return jsonify({
            'status': 'healthy',
            'message': 'Backend is running',
            'timestamp': datetime.now().isoformat(),
            'email_config': 'valid' if email_config_valid else 'invalid',
            'environment': os.environ.get('FLASK_ENV', 'development')
        })
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return jsonify({
            'status': 'unhealthy',
            'message': str(e)
        }), 500

@app.route('/', methods=['GET'])
def home():
    """Home page with API documentation"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Apology App Backend</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; }
            .endpoint { background: #f5f5f5; padding: 10px; margin: 10px 0; border-radius: 5px; }
            .method { color: #007bff; font-weight: bold; }
        </style>
    </head>
    <body>
        <h1>🚀 Apology App Backend</h1>
        <p>Backend is running successfully on Render!</p>
        
        <h2>Available Endpoints:</h2>
        
        <div class="endpoint">
            <span class="method">POST</span> <code>/send-notification</code>
            <p>Send email notifications from the Flutter app</p>
            <p><strong>Body:</strong> <code>{"name": "string", "action": "string"}</code></p>
        </div>
        
        <div class="endpoint">
            <span class="method">GET</span> <code>/health</code>
            <p>Health check endpoint for monitoring</p>
        </div>
        
        <div class="endpoint">
            <span class="method">GET</span> <code>/</code>
            <p>This documentation page</p>
        </div>
        
        <h2>Environment:</h2>
        <p>Environment: <strong>{}</strong></p>
        <p>Timestamp: <strong>{}</strong></p>
        
        <h2>Configuration Status:</h2>
        <p>Email Config: <strong>{}</strong></p>
    </body>
    </html>
    """.format(
        os.environ.get('FLASK_ENV', 'development'),
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'Valid' if all([SENDER_EMAIL, APP_PASSWORD, RECEIVER_EMAIL]) else 'Invalid'
    )

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({
        'status': 'error',
        'message': 'Endpoint not found'
    }), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    logger.error(f"Internal server error: {error}")
    return jsonify({
        'status': 'error',
        'message': 'Internal server error'
    }), 500

if __name__ == '__main__':
    # Get port from environment variable (Render sets this automatically)
    port = int(os.environ.get('PORT', 5000))
    
    # Set debug mode based on environment
    debug_mode = os.environ.get('FLASK_ENV') != 'production'
    
    logger.info(f"Starting server on port {port}")
    logger.info(f"Debug mode: {debug_mode}")
    logger.info(f"Environment: {os.environ.get('FLASK_ENV', 'development')}")
    
    app.run(
        host='0.0.0.0', 
        port=port, 
        debug=debug_mode
    )
