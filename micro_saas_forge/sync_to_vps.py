import os
import sys
import requests
import json
import logging
from typing import List
from titan_config import env

logging.basicConfig(level=logging.INFO, format='%(asctime)s - [SYNC] - %(message)s')

def sync_to_vps(files_to_sync: List[str]):
    """Reads local files and sends them to the Cloud Relay for hot-swapping."""
    # Settings
    vps_url = env("TITAN_RELAY_URL", "http://127.0.0.1:5000")
    secret_key = env("TITAN_RELAY_KEY", "titan-vanguard-relay-alpha-99x-CHANGE-THIS-IN-PROD")
    endpoint = f"{vps_url}/system/update"
    
    logging.info(f"🚀 Preparing to sync {len(files_to_sync)} files to VPS: {vps_url}")
    
    payload = {"files": {}}
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    for filename in files_to_sync:
        filepath = os.path.join(base_dir, filename)
        if not os.path.exists(filepath):
            logging.error(f"❌ File not found locally: {filename}")
            continue
            
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
            payload["files"][filename] = content
            logging.info(f"  📦 Packaged: {filename} ({len(content)} bytes)")
        except Exception as e:
            logging.error(f"❌ Error reading {filename}: {e}")
            
    if not payload["files"]:
        logging.warning("No files to sync. Aborting.")
        return
        
    # Send to VPS
    headers = {
        "X-Titan-Key": secret_key,
        "Content-Type": "application/json"
    }
    
    logging.info("📡 Transmitting payload across the wire...")
    try:
        response = requests.post(endpoint, json=payload, headers=headers, timeout=15)
        if response.status_code == 200:
            result = response.json()
            logging.info(f"✅ Remote VPS successfully hot-swapped {len(result.get('files', []))} files!")
            for tf in result.get('files', []):
                logging.info(f"  [VPS] Overwrote: {tf}")
        elif response.status_code == 401:
            logging.error("❌ Authentication Failed: Check your TITAN_RELAY_KEY.")
        else:
            logging.error(f"❌ Sync Failed: HTTP {response.status_code}")
            logging.error(response.text)
    except requests.exceptions.RequestException as e:
        logging.error(f"💥 Connection to Cloud Relay failed: {e}")

if __name__ == "__main__":
    # Default stack to keep synchronized
    TARGET_FILES = [
        "twitter_nurturer.py",
        "playwright_bot.py",
        "cloud_relay_node.py" # Inception: Syncing the relay node itself (will require manual restart on VPS to take effect)
    ]
    
    # Check args
    if len(sys.argv) > 1:
        TARGET_FILES = sys.argv[1:]
        
    sync_to_vps(TARGET_FILES)
