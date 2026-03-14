from flask import Flask, request, jsonify
import time
import logging
import os

# ==============================================================================
# TITAN ENGINE - CLOUD RELAY NODE (The "Hand")
# ==============================================================================
# This is a dumb relay server meant to run on the US VPS.
# It has zero intelligence. It only receives pre-computed payloads from the 
# Local Brain and executes the HTTP requests (or Playwright tasks) using the 
# pure US residential/datacenter IP to avoid shadowbans on Reddit/X.
# ==============================================================================

app = Flask(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - [%(levelname)s] - %(message)s')

# SECURITY: Shared secret. 
# The Local Brain must send this in the header. MUST read from env variable in production to prevent leakage.
SECRET_CLAW_KEY = os.environ.get("TITAN_RELAY_KEY", "titan-vanguard-relay-alpha-99x-CHANGE-THIS-IN-PROD")

if SECRET_CLAW_KEY == "titan-vanguard-relay-alpha-99x-CHANGE-THIS-IN-PROD":
    logging.warning("🚨 [SECURITY WARNING]: Using default hardcoded SECRET_CLAW_KEY. You MUST set TITAN_RELAY_KEY environment variable!")

def verify_request():
    token = request.headers.get("X-Titan-Key")
    if token != SECRET_CLAW_KEY:
        logging.warning(f"Unauthorized intrusion attempt from {request.remote_addr}")
        return False
    return True

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "Cloud Relay Node is ALIVE and holding the line."}), 200

@app.route('/publish/reddit', methods=['POST'])
def publish_reddit():
    """
    Receives text and target URL, then posts it to Reddit using US IP.
    (Requires Reddit API credentials configured on this VPS)
    """
    if not verify_request(): return jsonify({"error": "Unauthorized"}), 401
    
    data = request.json
    target_subreddit = data.get("subreddit")
    target_thread = data.get("thread_url")
    content = data.get("content")
    
    logging.info(f"Received payload from Brain. Target: {target_thread}")
    logging.info(f"Executing physical post via Playwright...")
    
    import subprocess
    try:
        # 召唤物理无头浏览器前去点火发帖
        result = subprocess.run(
            ["python", "playwright_bot.py", "--platform", "reddit", "--url", target_thread, "--content", content],
            capture_output=True, text=True, check=True
        )
        logging.info(f"Playwright Engine Output:\n{result.stdout}")
    except subprocess.CalledProcessError as e:
        logging.error(f"Playwright Execution Failed:\n{e.stderr}\n{e.stdout}")
        return jsonify({
            "error": "Failed to physically publish payload. Check bot logs.",
            "details": f"STDOUT:\n{e.stdout}\nSTDERR:\n{e.stderr}"
        }), 500
    
    logging.info(f"✅ Successfully injected affiliate payload into {target_subreddit}")
    return jsonify({
        "status": "success", 
        "message": "Payload delivered from US IP.",
        "reddit_url": f"{target_thread}/comment_mock_123"
    }), 200


@app.route('/publish/twitter', methods=['POST'])
def publish_twitter():
    """
    Receives text and posts a tweet using US IP via physical Playwright.
    """
    if not verify_request(): return jsonify({"error": "Unauthorized"}), 401
    
    data = request.json
    tweet_text = data.get("text")
    reply_text = data.get("reply_text")
    
    logging.info(f"Received Tweet payload from Brain. Length: {len(tweet_text)}")
    logging.info(f"Executing physical Tweet via Playwright...")

    import subprocess
    try:
        # Physical browser automation to simulate a real user typing and posting
        cmd = ["python", "playwright_bot.py", "--platform", "twitter", "--content", tweet_text]
        if reply_text:
            cmd.extend(["--reply", reply_text])
            
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        logging.info(f"Playwright Engine Output:\n{result.stdout}")
    except subprocess.CalledProcessError as e:
        logging.error(f"Playwright Twitter Failed:\n{e.stderr}\n{e.stdout}")
        return jsonify({
            "error": "Failed to physically publish tweet. Check bot logs.",
            "details": f"STDOUT:\n{e.stdout}\nSTDERR:\n{e.stderr}"
        }), 500

    logging.info(f"✅ Successfully tweeted payload.")
    return jsonify({"status": "success", "message": "Tweet published successfully via Playwright."}), 200

@app.route('/nurture/twitter', methods=['POST'])
def nurture_twitter():
    """
    Receives a request to start a Twitter nurturing session on the VPS.
    """
    if not verify_request(): return jsonify({"error": "Unauthorized"}), 401
    
    data = request.json or {}
    duration = data.get("duration", 5)
    
    logging.info(f"Received Nurture command from Brain. Duration: {duration} mins")
    logging.info(f"Executing physical Nurturing via Playwright...")

    import subprocess
    try:
        # Run the nurturer script in the background or wait for it.
        # It's better to wait_for it if the HTTP timeout allows, or run asynchronously.
        # Since it takes X minutes, we should run it decoupled, or return immediate success that it started.
        subprocess.Popen(
            ["python", "twitter_nurturer.py", "--duration", str(duration)],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
    except Exception as e:
        logging.error(f"Playwright Nurturer Failed to start:\n{e}")
        return jsonify({"error": "Failed to start nurturing process on VPS."}), 500

    logging.info(f"✅ Successfully started nurturing session.")
    return jsonify({"status": "success", "message": f"Nurturing session started for {duration} minutes."}), 200

@app.route('/system/update', methods=['POST'])
def system_update():
    """
    Receives JSON payload containing filenames and their raw source code.
    Overwrites the local python scripts to allow instantaneous remote deploys.
    """
    if not verify_request(): return jsonify({"error": "Unauthorized"}), 401
    
    data = request.json
    if not data or "files" not in data:
        return jsonify({"error": "Missing 'files' in payload"}), 400
        
    logging.warning("⚠️ Received SYSTEM UPDATE command from Brain. Overwriting local scripts...")
    
    updated_files = []
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    for filename, code_content in data["files"].items():
        # SECURITY: Prevent path traversal attacks (e.g. "../../../etc/passwd" or absolute paths)
        clean_filename = os.path.basename(filename)
        
        # Only allow updating python files
        if not clean_filename.endswith('.py'):
            logging.warning(f"Rejected update for non-python file: {clean_filename}")
            continue
            
        target_path = os.path.join(base_dir, clean_filename)
        try:
            with open(target_path, "w", encoding="utf-8") as f:
                f.write(code_content)
            updated_files.append(clean_filename)
            logging.info(f"  ✅ Updated: {clean_filename}")
        except Exception as e:
            logging.error(f"  ❌ Failed to update {clean_filename}: {e}")
            
    return jsonify({
        "status": "success",
        "message": f"Successfully hot-swapped {len(updated_files)} files.",
        "files": updated_files
    }), 200

if __name__ == '__main__':
    logging.info("Starting Titan Cloud Relay Node on 0.0.0.0:5000...")
    logging.warning("🚨 [SECURITY DANGER]: Running exposed HTTP directly! Key can be MITM intercepted.")
    logging.warning("👉 [ACTION REQUIRED]: Please bind to 127.0.0.1 and use SSH tunneling, or put Caddy/Nginx HTTPS reverse proxy in front!")
    # Runs on port 5000, accessible from anywhere
    app.run(host='0.0.0.0', port=5000)
