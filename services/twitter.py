import sys
import requests
import tweepy

import configs.setup_config as config
import states.app_state as state
import utils.common as utils

MY_CLIENT = None


# Check presence of tokens in response
def check_tokens(access_token, refresh_token):
    if not access_token:
        print("Error: No access token in response")
        print(f"Response: {access_token}")
        sys.exit(1)

    if not refresh_token:
        print(
            "Error: No refresh token received. Make sure 'offline.access' scope is included."
        )
        print(f"Response: {refresh_token}")
        sys.exit(1)

    print("✓ Tokens received successfully")


# return tweepy.Client instance
def my_client() -> tweepy.Client:
    global MY_CLIENT

    access_token = state.get_access_token()

    if access_token:
        MY_CLIENT = tweepy.Client(access_token)
        return MY_CLIENT

    if "MY_CLIENT" in globals():
        return MY_CLIENT


# Exchange authorization code for tokens
def exchange_code_for_token(code: str):
    data = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": config.REDIRECT_URI,
        "code_verifier": config.CODE_VERIFIER,
        "client_id": config.X_CLIENT_ID,
    }

    return request_token(data)


# Request token from X API
def request_token(data={}):
    # Prepare token request
    token_url = "https://api.x.com/2/oauth2/token"
    token = utils.encode_basic_token(config.X_CLIENT_ID, config.X_CLIENT_SECRET)
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Authorization": f"Basic {token}",
    }

    try:
        response = requests.post(token_url, data=data, headers=headers)
        response.raise_for_status()

        token_data = response.json()

        return token_data
    except requests.exceptions.RequestException as e:
        print(f"Error requesting token: {e}")
        raise e


# Get authenticated user info
# Rate limit: 25 requests / 24 hours PER USER
def get_my_info():
    params = {"tweet_fields": ["created_at"], "user_auth": False}

    try:
        response = my_client().get_me(**params)
    except tweepy.TweepyException as e:
        print(f"Error fetching user info: {e}")
        raise e

    return response
