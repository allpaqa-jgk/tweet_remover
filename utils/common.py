import sys
import base64


def encode_basic_token(client_id, client_secret):
    """Encode client ID and secret into a Basic Auth token."""
    token = f"{client_id}:{client_secret}"
    return base64.b64encode(token.encode()).decode()
