import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

NUM_TO_FETCH = 100
NUM_TO_DELETE = 100
REMOVE_TWEETS_BATCH_SIZE = 10
REMOVE_RETWEETS_BATCH_SIZE = 1
WEBHOOK_EVENTS = ["task_failed", "task_succeeded"]  # "task_failed", "task_succeeded"

# OAuth2 configuration
GH_TOKEN = os.environ.get("GH_TOKEN")
X_CLIENT_ID = os.environ.get("X_CLIENT_ID")
X_CLIENT_SECRET = os.environ.get("X_CLIENT_SECRET")
X_ACCESS_TOKEN = os.environ.get("X_ACCESS_TOKEN", "")
X_REFRESH_TOKEN = os.environ.get("X_REFRESH_TOKEN")
X_USER_ID = os.environ.get("X_USER_ID", "__None__")
X_CUTOFF_DAYS = int(os.environ.get("X_CUTOFF_DAYS", "14"))
X_UNTIL_ID = os.environ.get("X_UNTIL_ID", "__None__")
X_TARGET_IDS_JSON = os.environ.get("X_TARGET_IDS_JSON", "[]")
WEBHOOK_URL = os.environ.get("WEBHOOK_URL", "")
