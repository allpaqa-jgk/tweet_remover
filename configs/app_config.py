import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

NUM_TO_DELETE = 10

# OAuth2 configuration
GH_TOKEN = os.environ.get("GH_TOKEN")
X_CLIENT_ID = os.environ.get("X_CLIENT_ID")
X_CLIENT_SECRET = os.environ.get("X_CLIENT_SECRET")
X_ACCESS_TOKEN = os.environ.get("X_ACCESS_TOKEN", "")
X_REFRESH_TOKEN = os.environ.get("X_REFRESH_TOKEN")
X_USER_ID = os.environ.get("X_USER_ID", "__NONE__")
X_CUTOFF_DAYS = int(os.environ.get("X_CUTOFF_DAYS", "14"))
X_UNTIL_ID = os.environ.get("X_UNTIL_ID", "__NONE__")
WEBHOOK_URL = os.environ.get("WEBHOOK_URL", "")
