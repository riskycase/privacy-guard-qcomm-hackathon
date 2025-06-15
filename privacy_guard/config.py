# Configuration for API endpoints
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# API endpoints
FACE_API_URL = os.environ.get("FACE_API_URL", "http://localhost:5000/api/faces")
LLM_URL = os.environ.get("LLM_URL", "http://localhost:3001/api/v1/openai/chat/completions")
WORKSPACE_NAME = os.environ.get("WORKSPACE_NAME", "default")

# API authentication
API_TOKEN = os.environ.get("API_TOKEN", "")
