import json
import sys
import base64

import configs.app_config as app_config
import states.app_state as app_state
import services.github as github_service
import services.discord as discord_service


def encode_basic_token(client_id, client_secret):
    """Encode client ID and secret into a Basic Auth token."""
    token = f"{client_id}:{client_secret}"
    return base64.b64encode(token.encode()).decode()


def exec_with_discord_notification(func, *args, **kwargs):
    try:
        func(*args, **kwargs)
        if "task_succeeded" in app_config.WEBHOOK_EVENTS:
            discord_service.send_message("✅ Batch process completed successfully.")
    except Exception as e:
        if "task_failed" in app_config.WEBHOOK_EVENTS:
            discord_service.send_message(f"❌ Error in batch process: {e}")

        print(f"Error in batch process: {e}")
        if "--debug" in sys.argv:
            import traceback

            traceback.print_exc()

        sys.exit(1)


def print_secret(value, label=None):
    """Print a secret to logs with smart masking and optional label.

    Shows a prefix in clear text for debugging while masking the full secret.
    Automatically determines prefix length as 20% of secret length (minimum 4, maximum 8).
    Secrets shorter than 8 chars are fully masked for security.

    Args:
        value: The secret value to mask and print
        label: Optional label to print before the masked value (e.g., "Client ID")
    """

    str_value = str(value)
    if not str_value or str_value == "__None__":
        # Don't mask "__None__" as it would mask all zeros in logs
        if label:
            print(f"{label}: (not set)")
        return

    # Mask the full secret so it won't appear accidentally in logs
    print(f"::add-mask::{str_value}", flush=True)

    # Calculate prefix length as 20% of value length
    value_len = len(str_value)
    if value_len < 8:
        # Too short - mask everything for security
        prefix_len = 0
    else:
        # Use 20% of length, with min 4 and max 8
        prefix_len = max(4, min(8, int(value_len * 0.2)))

    # Create the display string with visible prefix
    if prefix_len > 0:
        # Show prefix in clear text for debugging, rest as asterisks
        masked_value = str_value[:prefix_len] + "***"
    else:
        # Don't show anything for short secrets
        masked_value = "***"

    # Print with optional label
    if label:
        print(f"{label}: {masked_value}")
    else:
        print(masked_value)


def debug_print(value, label=None):
    """Print debug information if --debug flag is set.

    Args:
        value: The value to print
        label: Optional label to print before the value
    """
    if "--debug" in sys.argv:
        if label:
            print(f"{label}: {value}")
        else:
            print(value)


# get tweet IDs from app_state.tweets
# [{type: "tweet"/"retweet", id: str}, ...]
def get_tweet_ids() -> list[dict[str, str]]:
    """Get tweet IDs from app state."""
    return app_state.get_tweets()


# update app_state.tweets and save to Github Secrets
# [{type: "tweet"/"retweet", id: str}, ...]
def set_tweet_ids(tweets: list[dict[str, str]]) -> None:
    tweets_json = json.dumps(tweets)
    app_state.set_tweets(tweets)
    github_service.save_target_ids(tweets)
    # TODO: Remove set_github_variable for X_TARGET_IDS_JSON after check on Github Actions
    github_service.set_github_variable("X_TARGET_IDS_JSON", tweets_json)
    debug_print(tweets_json, "Updated tweet IDs JSON")
