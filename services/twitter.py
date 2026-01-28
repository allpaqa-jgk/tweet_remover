import sys
import requests
from datetime import datetime, timedelta, timezone
import tweepy
from pprint import pprint

import configs.setup_config as config
import states.app_state as state
import utils.common as utils
import services.github as github

MY_CLIENT = None


# Check presence of tokens in response
def check_tokens(access_token: str, refresh_token: str) -> None:
    if not access_token:
        print("Error: No access token in response")
        print(f"Response: {access_token}")
        raise Exception("No access token received")

    if not refresh_token:
        print(
            "Error: No refresh token received. Make sure 'offline.access' scope is included."
        )
        print(f"Response: {refresh_token}")
        raise Exception("No refresh token received")

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

    """Create and return authenticated Twitter client."""

    try:
        token_data = exchange_refresh_token()
        access_token = token_data.get("access_token")
        refresh_token = token_data.get("refresh_token")
        check_tokens(access_token, refresh_token)

        if "access_token" not in token_data:
            print("Error: Failed to refresh access token")
            print(f"Response: {token_data}")
            raise Exception("Failed to refresh access token")

        print(f"✓ Authentication successful")
        access_token = token_data["access_token"]
        utils.print_secret(access_token, "Access token refreshed")
        state.set_access_token(access_token)

        # Update refresh token if a new one was provided
        new_refresh_token = refresh_token
        if new_refresh_token and new_refresh_token != config.X_REFRESH_TOKEN:
            utils.print_secret(new_refresh_token, "New refresh token received")
            github.set_github_variable("X_REFRESH_TOKEN", new_refresh_token)

            if "--debug" in sys.argv:
                pprint(token_data)

        # Create client with access token
        MY_CLIENT = tweepy.Client(access_token)

        return MY_CLIENT
    except requests.exceptions.RequestException as e:
        print(f"Error refreshing token: {e}")
        if (
            hasattr(e, "response")
            and e.response is not None
            and hasattr(e.response, "text")
        ):
            print(f"Response: {e.response.text}")
            # Check if it's an authentication error (invalid/expired/revoked token)
            if hasattr(e, "response") and e.response is not None:
                status_code = e.response.status_code
                if status_code in [400, 401]:  # Bad Request or Unauthorized
                    print("⚠ Refresh token appears to be invalid, expired, or revoked")
                    print("Wiping secrets to prevent repeated failures on next run")
                    print("Please run setup_secret.py again to re-authenticate")
                    # Wipe the secrets so next run knows setup is needed
                    github.set_github_variable("X_REFRESH_TOKEN", "__None__")
                    github.set_github_variable("X_UNTIL_ID", "__None__")
        raise Exception("Failed to refresh access token") from e
    except Exception as e:
        print(f"Error refreshing token: {e}")
        raise e


# Exchange authorization code for tokens
def exchange_code_for_token(code: str) -> dict:
    data = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": config.REDIRECT_URI,
        "code_verifier": config.CODE_VERIFIER,
        "client_id": config.X_CLIENT_ID,
    }

    try:
        response = request_token(data)
    except requests.exceptions.RequestException as e:
        print(f"Error exchanging code for token: {e}")
        raise e

    return response


# Exchange refresh token for new access token
def exchange_refresh_token() -> dict:
    data = {
        "grant_type": "refresh_token",
        "refresh_token": config.X_REFRESH_TOKEN,
        "client_id": config.X_CLIENT_ID,
    }

    try:
        response = request_token(data)
    except requests.exceptions.RequestException as e:
        print(f"Error exchanging refresh token for new access token: {e}")
        raise e

    return response


# Request token from X API
def request_token(data: dict = {}) -> dict:
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
    except requests.exceptions.RequestException as e:
        print(f"Error requesting token: {e}")
        raise e

    return token_data


# Get authenticated user info
# Rate limit: 25 requests / 24 hours PER USER
def get_my_info() -> tweepy.Response | requests.models.Response:
    params = {"tweet_fields": ["created_at"], "user_auth": False}

    try:
        response = my_client().get_me(**params)
    except tweepy.TweepyException as e:
        print(f"Error fetching user info: {e}")
        raise e

    return response


# Rate limit: 1 requests / 15 mins PER USER
def get_my_tweets() -> tweepy.Response | requests.models.Response:
    # Get configurable cutoff days (default to 14)
    if config.X_USER_ID == "__None__":
        print("Error: X_USER_ID is not set")
        raise Exception("X_USER_ID is not set")

    if config.X_CUTOFF_DAYS:
        cutoff_days = int(config.X_CUTOFF_DAYS)
    else:
        cutoff_days = 14
    print(f"Configuration: Delete tweets older than {cutoff_days} days")

    # Calculate cutoff date
    cutoff_date = datetime.now(timezone.utc) - timedelta(days=cutoff_days)
    print(f"Cutoff date: {cutoff_date.isoformat()}")

    # Fetch user's tweets
    # Use end_time to filter to only tweets older than cutoff_date
    # This makes the API call more efficient by only fetching deletion candidates
    params = {
        "id": config.X_USER_ID,
        "max_results": config.NUM_TO_DELETE,  # max = 100
        "tweet_fields": [
            "created_at",
            "referenced_tweets",
            "author_id",
        ],
        "end_time": cutoff_date.strftime("%Y-%m-%dT%H:%M:%SZ"),  # RFC3339
        "user_auth": False,
        "expansions": "referenced_tweets.id",
    }

    # Use until_id for pagination if we have one and it's not "__None__"
    if config.X_UNTIL_ID and config.X_UNTIL_ID != "__None__":
        params["until_id"] = config.X_UNTIL_ID

    try:
        utils.debug_print(params, "Fetching tweets with params")
        result = my_client().get_users_tweets(**params)
        utils.debug_print(result, "Fetched tweets response")
    except tweepy.TweepyException as e:
        print(f"Error fetching tweets: {e}")
        raise e
    return result


# Rate limit: 17 requests / 24 hours PER USER
#             17 requests / 24 hours PER APP
def delete_my_tweet(id: str) -> tweepy.Response | requests.models.Response:
    params = {
        "id": id,
        "user_auth": False,
    }
    return my_client().delete_tweet(**params)


# Rate limit: 1 requests / 15 mins PER USER
def delete_my_retweet(id: str) -> tweepy.Response | requests.models.Response:
    params = {
        "source_tweet_id": id,
        "user_auth": False,
    }
    return my_client().unretweet(**params)
