import subprocess
import sys
import os
from pathlib import Path
from db import Database

def check_database():
    db = Database()
    try:
        articles = db.get_articles()
        summaries = db.get_summaries()
        settings = db.get_settings()
        print(f"Database check: Found {len(articles)} articles and {len(summaries)} summaries")
    except Exception as e:
        print(f"Database check failed: {e}")
        sys.exit(1)

def start_services():
    # Check database first
    check_database()
    
    # Get the directory containing this script
    root_dir = Path(__file__).parent
    web_dir = root_dir / "narrate-news-web"
    
    try:
        # Start the FastAPI server
        api_process = subprocess.Popen(
            [sys.executable, "-m", "uvicorn", "api.main:app", "--reload", "--port", "8000"],
            cwd=root_dir
        )
        
        # Start the Next.js development server
        npm_process = subprocess.Popen(
            ["npm", "run", "dev"],
            cwd=web_dir
        )
        
        # Wait for both processes
        api_process.wait()
        npm_process.wait()
        
    except KeyboardInterrupt:
        print("\nShutting down services...")
        api_process.terminate()
        npm_process.terminate()
        sys.exit(0)
    except Exception as e:
        print(f"Error starting services: {e}")
        sys.exit(1)

if __name__ == "__main__":
    start_services()