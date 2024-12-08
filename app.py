from flask import Flask, request, jsonify
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import random
import os
import logging

app = Flask(__name__)

# Setting up logging
logging.basicConfig(level=logging.INFO)

# Environment variables for configuration
SENDER_EMAIL = os.getenv('SENDER_EMAIL', 'capstonebpresentation@gmail.com')
SENDER_PASSWORD = os.getenv('SENDER_PASSWORD', 'luomnnahalgrxpvh')  # Default fallback password

# Store OTPs with email as key
otps = {}

def send_email(recipient_email, otp):
    recipient_name = 'Recipient Name'  # This can be dynamically fetched or sent by the client

    message = MIMEMultipart()
    message['From'] = SENDER_EMAIL
    message['To'] = recipient_email
    message['Subject'] = 'Your OTP'

    body = f"Hello {recipient_name},\nYour OTP is: {otp}\n\nBest regards,\nYour Team"
    message.attach(MIMEText(body, 'plain'))

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.sendmail(SENDER_EMAIL, recipient_email, message.as_string())
        server.quit()
        logging.info(f"OTP sent to {recipient_email}")
    except Exception as e:
        logging.error(f"Failed to send email: {str(e)}")
        return False  # Indicate failure

    return True

@app.route('/send_otp', methods=['POST'])
def handle_send_otp():
    email = request.json.get('email')
    if not email:
        return jsonify({'error': 'Email is required'}), 400

    otp = str(random.randint(100000, 999999))
    otps[email] = otp
    if not send_email(email, otp):
        return jsonify({'error': 'Failed to send OTP'}), 500

    return jsonify({'message': 'OTP sent successfully'}), 200

@app.route('/validate_otp', methods=['POST'])
def handle_validate_otp():
    email = request.json.get('email')
    otp = request.json.get('otp')
    if not email or not otp:
        return jsonify({'error': 'Email and OTP are required'}), 400

    if otps.get(email) == otp:
        return jsonify({'status': 'valid'}), 200
    else:
        return jsonify({'status': 'invalid'}), 200

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Server error'}), 500

if __name__ == '__main__':
    app.run(debug=True)
