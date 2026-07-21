import os, sys
from dotenv import load_dotenv

# Load local environment variables if testing locally
load_dotenv()

# --- CONFIGURATION & SECURITY GATEKEEPER ---
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
MODEL_NAME = "gemini-3.1-flash-lite"
DB_NAME = "review_history.db"

if not GEMINI_API_KEY:
    print("Configuration Error: GEMINI_API_KEY environment variable is missing!")
    sys.exit(1)
    