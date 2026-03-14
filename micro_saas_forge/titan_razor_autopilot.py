import os
import sys
import time
import logging
import subprocess
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def run_script(script_name: str) -> bool:
    """Run a Python script and return True if successful."""
    script_path = os.path.join(BASE_DIR, script_name)
    if not os.path.exists(script_path):
        logging.error(f"Script not found: {script_path}")
        return False
        
    logging.info(f"🚀 Starting module: {script_name}...")
    start_time = time.time()
    
    try:
        # Run the script and stream output
        process = subprocess.run(
            [sys.executable, script_path],
            cwd=BASE_DIR,
            check=True,
            text=True,
            capture_output=False # Let it print to console naturally
        )
        
        elapsed = time.time() - start_time
        logging.info(f"✅ Module {script_name} completed successfully in {elapsed:.1f}s.\n")
        return True
    
    except subprocess.CalledProcessError as e:
        logging.error(f"❌ Module {script_name} failed with exit code {e.returncode}.")
        return False
    except Exception as e:
        logging.error(f"❌ Unexpected error running {script_name}: {e}")
        return False

def main():
    print("="*60)
    print(f"🚢 TITAN RAZOR AUTOPILOT - GLOBAL EDITION (US MARKET)")
    print(f"⏰ Session Start: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}")
    print("="*60)
    print("\nStarting the automated Pipeline: Crawler -> Analyzer -> Publisher\n")
    
    total_start_time = time.time()
    
    # Define the 3-step pipeline
    pipeline = [
        "pipeline_crawler.py",
        "titan_analyzer.py",
        "static_publisher.py"
    ]
    
    for step in pipeline:
        success = run_script(step)
        if not success:
            logging.error(f"Pipeline ABORTED due to failure in {step}.")
            sys.exit(1)
            
    total_elapsed = time.time() - total_start_time
    
    print("="*60)
    print(f"🎉 GLOBAL PIPELINE COMPLETED DIFFERENTIALLY IN {total_elapsed:.1f} SECONDS")
    print("="*60)
    
    # Path to the generated index
    output_html = os.path.join(BASE_DIR, "shipmicro_site", "public", "index_global.html")
    print(f"\nYour static site is ready at:\n➡️  {output_html}\n")
    print("To preview the site, you can open this file in your browser.")
    
    # Optional: Open the file automatically on Windows/Mac
    try:
        if sys.platform == "win32":
            os.startfile(output_html)
        elif sys.platform == "darwin":
            subprocess.run(["open", output_html])
    except Exception as e:
        logging.warning("Could not automatically open browser.", exc_info=True)

if __name__ == "__main__":
    main()
