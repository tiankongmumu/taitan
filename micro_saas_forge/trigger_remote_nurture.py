import os
import sys
import requests
import json
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - [TRIGGER] - %(message)s')

from titan_config import env

def trigger_remote_nurture(duration_minutes=5):
    # Retrieve VPS IP or Domain from environment
    vps_url = env("TITAN_RELAY_URL", "http://127.0.0.1:5000") # USER SHOULD SET THIS IN .env
    secret_key = env("TITAN_RELAY_KEY", "titan-vanguard-relay-alpha-99x-CHANGE-THIS-IN-PROD")
    
    endpoint = f"{vps_url}/nurture/twitter"
    
    headers = {
        "X-Titan-Key": secret_key,
        "Content-Type": "application/json"
    }
    
    payload = {
        "duration": duration_minutes
    }
    
    logging.info(f"Sending Nurture command to Cloud Relay: {endpoint}")
    try:
        response = requests.post(endpoint, json=payload, headers=headers, timeout=10)
        if response.status_code == 200:
            logging.info("✅ Remote VPS has successfully started the Nurturing session.")
            logging.info(f"Response: {response.json()}")
        else:
            logging.error(f"❌ Failed to trigger Cloud Relay: HTTP {response.status_code}")
            logging.error(response.text)
    except requests.exceptions.RequestException as e:
        logging.error(f"💥 Connection to Cloud Relay failed: {e}")

if __name__ == "__main__":
    trigger_remote_nurture(duration_minutes=6)
