import hashlib
import base64
import secrets

from configs.app_config import *

# OAuth2 configuration
REDIRECT_URI = "http://localhost:8080/callback"
SCOPES = ["tweet.read", "tweet.write", "users.read", "offline.access"]


# Generate code verifier and challenge for PKCE
CODE_VERIFIER = (
    base64.urlsafe_b64encode(secrets.token_bytes(32)).decode("utf-8").rstrip("=")
)
CODE_CHALLENGE = (
    base64.urlsafe_b64encode(hashlib.sha256(CODE_VERIFIER.encode("utf-8")).digest())
    .decode("utf-8")
    .rstrip("=")
)
