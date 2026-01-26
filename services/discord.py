import requests
from configs.app_config import WEBHOOK_URL


def send_message(content: str) -> bool:
    """Send a message to Discord via webhook."""
    if not WEBHOOK_URL:
        print("Discord webhook URL not configured.")
        return False

    data = {"content": content}

    try:
        response = requests.post(WEBHOOK_URL, json=data)
        response.raise_for_status()
        print("✓ Message sent to Discord successfully.")
        return True
    except requests.exceptions.RequestException as e:
        print(f"Error sending message to Discord: {e}")
        return False
