from flask import Flask, request, jsonify
from flask_compress import Compress
import os
import smtplib
from email import message_from_string

app = Flask(__name__)

# Support for Accept-Encoding compressions
Compress(app)


@app.route('/sendmail_dryrun', methods=['POST'])
def sendmail_dryrun():
    # Environment variables
    smtp_server, smtp_port, smtp_user, smtp_password, api_key = loadEnvironmentVars()
    if smtp_server is None:
        return jsonify({"success": 0, "error": "Env vars not set up."}), 500

    # Interpret data
    data = request.get_json()

    # Check API key
    if data.get('api_key') != api_key:
        return jsonify({"success": 0, "error": "Wrong api_key."}), 401

    msg_encoding = data.get('encoding')
    msg_raw = data.get('raw')

    msg_decoded = decodeMessage(msg_raw, msg_encoding)

    return (msg_decoded.as_string()), 200


@app.route('/sendmail', methods=['POST'])
def sendmail():
    # Environment variables
    smtp_server, smtp_port, smtp_user, smtp_password, api_key = loadEnvironmentVars()
    if smtp_server is None:
        return jsonify({"success": 0, "error": "Env vars not set up."}), 500

    # Interpret data
    data = request.get_json()

    # Check API key
    if data.get('api_key') != api_key:
        return jsonify({"success": 0, "error": "Wrong api_key."}), 401

    envelope_from = data.get('envelope_from')
    envelope_to = data.get('envelope_to')
    msg_encoding = data.get('encoding')
    msg_raw = data.get('raw')

    msg_decoded = decodeMessage(msg_raw, msg_encoding)

    msg = message_from_string(msg_decoded)

    try:
        # Intentional to start a SSL/TLS connection, not STARTTLS
        with smtplib.SMTP_SSL(smtp_server, smtp_port) as server:
            server.login(smtp_user, smtp_password)
            server.sendmail(envelope_from, envelope_to, msg.as_string())
        return jsonify({"success": 1}), 200
    except Exception as e:
        return jsonify({"success": 0, "error": str(e)}), 500


@app.route('/health', methods=['GET'])
def health():
    # Environment variables
    smtp_server, smtp_port, smtp_user, smtp_password, api_key = loadEnvironmentVars()
    if smtp_server is None:
        return jsonify({"status": "unhealthy", "error": "Env vars not set up."}), 500
    
    # Test SMTP server
    try:
        # Establish connection to the SMTP server
        # Intentional to start a SSL/TLS connection, not STARTTLS
        with smtplib.SMTP_SSL(smtp_server, smtp_port) as server:
            server.login(smtp_user, smtp_password)
            # Send EHLO command to check server status
            response = server.ehlo()
        
        if response[0] != 250:
            return jsonify({"status": "unhealthy", "error": "SMTP server returned unexpected response.", "response": response}), 500
        
        return jsonify({"status": "healthy"}), 200

    except Exception as e:
        return jsonify({"status": "unhealthy", "error": f"Failed to reach STMP server: {str(e)}"}), 500



# Get secrets from the env vars. Must all be available.
def loadEnvironmentVars():
    smtp_server = os.environ.get('SMTP_SERVER')
    smtp_port = os.environ.get('SMTP_PORT')
    smtp_user = os.environ.get('SMTP_USER')
    smtp_password = os.environ.get('SMTP_PASSWORD')
    api_key = os.environ.get('API_KEY')
    if smtp_server is None or \
       smtp_port is None or \
       smtp_user is None or \
       smtp_password is None or \
       api_key is None:
        return None, None, None, None, None
    
    return smtp_server, smtp_port, smtp_user, smtp_password, api_key

def decodeMessage(msg_raw, msg_encoding):
    match msg_encoding:
        case "b64":
            import base64
            return base64.b64decode(msg_raw)
        case _: # include "string"
            return msg_raw



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)