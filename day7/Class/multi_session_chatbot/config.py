import os
from dotenv import load_dotenv

# Automatically look for and load the .env file
load_dotenv()

DB_NAME = os.getenv("DB_NAME")
DEFAULT_MODEL = os.getenv("DEFAULT_MODEL")
OLLAMA_API_BASE = os.getenv("OLLAMA_API_BASE", "http://localhost:11434")
