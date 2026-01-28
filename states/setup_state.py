import secrets

# OAuth2 configuration
state = secrets.token_urlsafe(16)
auth_code = None
