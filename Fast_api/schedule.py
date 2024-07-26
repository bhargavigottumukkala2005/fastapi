import requests
import json
import base64
import os
import logging
from flask import Flask, request, redirect, jsonify

# Set up logging
logging.basicConfig(level=logging.INFO)

app = Flask(__name__)

# Zoom OAuth credentials (replace with your actual credentials)
CLIENT_ID = os.getenv('CLIENT_ID', '_6KMf8b7RJuB10ydU_bKGA')
CLIENT_SECRET = os.getenv('CLIENT_SECRET', 'HbQRz9vf3hAFeqQXD1uat2biYCTYS4gh')
REDIRECT_URI = 'http://localhost:3000/callback'
TOKEN_FILE = 'zoom_tokens.json'

# Helper function to load tokens from a file
def load_tokens():
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, 'r') as f:
            return json.load(f)
    return {}

# Helper function to save tokens to a file
def save_tokens(tokens):
    with open(TOKEN_FILE, 'w') as f:
        json.dump(tokens, f)

# Function to refresh the access token
def refresh_access_token(refresh_token):
    token_url = "https://zoom.us/oauth/token"
    headers = {
        "Authorization": f"Basic {base64.b64encode((CLIENT_ID + ':' + CLIENT_SECRET).encode()).decode()}",
        "Content-Type": "application/x-www-form-urlencoded"
    }
    payload = {
        "grant_type": "refresh_token",
        "refresh_token": refresh_token
    }
    try:
        response = requests.post(token_url, headers=headers, data=payload)
        response.raise_for_status()  # Raise an exception for HTTP errors
        response_data = response.json()
        if 'access_token' in response_data:
            logging.info("Access token refreshed successfully.")
            save_tokens(response_data)
            return response_data.get("access_token")
        else:
            logging.error("Failed to refresh access token: %s", response_data)
            return None
    except requests.RequestException as e:
        logging.error("Error refreshing access token: %s", e)
        return None

# Function to schedule a meeting
def schedule_meeting(access_token):
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    
    meeting_details = {
        "topic": "Automated Meeting",
        "type": 2,  # Scheduled meeting
        "start_time": "2024-06-08T11:20:00Z",  # Meeting start time in ISO 8601 format
        "duration": 60,  # Duration in minutes
        "timezone": "UTC",
        "agenda": "This is an automated meeting",
        "settings": {
            "host_video": True,
            "participant_video": True,
            "join_before_host": False,
            "mute_upon_entry": True,
            "watermark": True,
            "use_pmi": False,
            "approval_type": 0,  # Automatically approve
            "registration_type": 1,  # Attendees register once and can attend any of the occurrences
            "audio": "both",  # Both telephony and VoIP
            "auto_recording": "cloud"
        }
    }
    
    user_id = 'me'  # Use 'me' for the authenticated user, or replace with a specific user ID
    try:
        response = requests.post(f'https://api.zoom.us/v2/users/{user_id}/meetings', headers=headers, json=meeting_details)
        response.raise_for_status()  # Raise an exception for HTTP errors
        meeting = response.json()
        join_url = meeting.get('join_url')
        return join_url
    except requests.RequestException as e:
        logging.error("Failed to schedule meeting: %s", e)
        return None

# Step 1: Get Authorization URL
@app.route('/')
def home():
    auth_url = (
        f"https://zoom.us/oauth/authorize?response_type=code&client_id={CLIENT_ID}"
        f"&redirect_uri={REDIRECT_URI}"
    )
    return redirect(auth_url)

# Step 2: Exchange Authorization Code for Access Token
@app.route('/callback')
def callback():
    code = request.args.get('code')
    token_url = "https://zoom.us/oauth/token"
    headers = {
        "Authorization": f"Basic {base64.b64encode((CLIENT_ID + ':' + CLIENT_SECRET).encode()).decode()}",
        "Content-Type": "application/x-www-form-urlencoded"
    }
    payload = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": REDIRECT_URI
    }
    try:
        response = requests.post(token_url, headers=headers, data=payload)
        response.raise_for_status()  # Raise an exception for HTTP errors
        response_data = response.json()
        if 'access_token' in response_data:
            save_tokens(response_data)
            access_token = response_data.get("access_token")
            join_url = schedule_meeting(access_token)
            if join_url:
                return redirect(join_url)
            else:
                return "Failed to schedule meeting."
        else:
            return "Failed to obtain access token."
    except requests.RequestException as e:
        logging.error("Error exchanging authorization code for access token: %s", e)
        return "An error occurred while processing your request."

# Step 3: Refresh Access Token (if needed)
@app.route('/refresh_token')
def refresh_token():
    tokens = load_tokens()
    if 'refresh_token' in tokens:
        new_access_token = refresh_access_token(tokens['refresh_token'])
        if new_access_token:
            return jsonify(access_token=new_access_token)
        else:
            return "Failed to refresh access token."
    else:
        return "No refresh token found."

if __name__ == "__main__":
    app.run(debug=True, port=3000)