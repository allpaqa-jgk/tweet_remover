import sys
import base64

import services.discord as discord_service


def encode_basic_token(client_id, client_secret):
    """Encode client ID and secret into a Basic Auth token."""
    token = f"{client_id}:{client_secret}"
    return base64.b64encode(token.encode()).decode()


def exec_with_discord_notification(func, *args, **kwargs):
    try:
        func(*args, **kwargs)
        discord_service.send_message("✅ Batch process completed successfully.")
    except Exception as e:
        discord_service.send_message(f"❌ Error in batch process: {e}")

        print(f"Error in batch process: {e}")
        if "--debug" in sys.argv:
            import traceback

            traceback.print_exc()

        sys.exit(1)
