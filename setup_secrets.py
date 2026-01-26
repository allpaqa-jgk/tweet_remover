#!/usr/bin/env python3
"""
Setup script for OAuth2 PKCE authentication with X (Twitter) API.
This script runs a local server to handle the OAuth callback and sets up
GitHub secrets using the gh CLI.
"""

import sys
import webbrowser
from urllib.parse import urlencode

import configs.setup_config as config
import states.setup_state as setup_state
import states.app_state as app_state
import services.github as github_service
import services.twitter as twitter_service

import utils.servers as servers


def check_config():
    # Check if secrets are configured
    if not config.X_CLIENT_ID:
        print("Error: X_CLIENT_ID environment variable not set")
        sys.exit(1)
    if not config.X_CLIENT_SECRET:
        print("Error: X_CLIENT_SECRET environment variable not set")
        sys.exit(1)

    if not github_service.get_github_auth_status():
        print(
            "Error: GH_TOKEN environment variable not set or invalid GitHub Personal Access Token"
        )
        sys.exit(1)


def authorize_url():
    # Build authorization URL
    auth_params = {
        "response_type": "code",
        "client_id": config.X_CLIENT_ID,
        "redirect_uri": config.REDIRECT_URI,
        "scope": " ".join(config.SCOPES),
        "state": setup_state.state,
        "code_challenge": config.CODE_CHALLENGE,
        "code_challenge_method": "S256",
    }

    auth_url = f"https://x.com/i/oauth2/authorize?{urlencode(auth_params)}"

    print(f"If browser doesn't open, visit: {auth_url}")
    return auth_url


def check_auth_code():
    if not setup_state.auth_code:
        print("Error: No authorization code received")
        sys.exit(1)

    print("✓ Authorization code received", setup_state.auth_code)


def input_cutoff_days():
    while True:
        cutoff_input = input("Please input ignored days (default 14 days): ").strip()
        if not cutoff_input:
            cutoff_days = "14"
            print("Using default: 14 days")
            break
        try:
            cutoff_value = int(cutoff_input)
            if cutoff_value < 1:
                print("Error: Please enter a positive number")
                continue
            cutoff_days = str(cutoff_value)
            print(f"Will delete tweets older than {cutoff_days} days")
            break
        except ValueError:
            print("Error: Please enter a valid number")
    return cutoff_days


def save_secrets(user_id, access_token, refresh_token, cutoff_days):
    success = True
    success &= github_service.set_github_secret("GH_TOKEN", config.GH_TOKEN)
    success &= github_service.set_github_secret("X_UNTIL_ID", config.X_UNTIL_ID)
    success &= github_service.set_github_secret("X_CLIENT_ID", config.X_CLIENT_ID)
    success &= github_service.set_github_secret(
        "X_CLIENT_SECRET", config.X_CLIENT_SECRET
    )
    success &= github_service.set_github_secret("X_USER_ID", str(user_id))
    success &= github_service.set_github_secret("X_REFRESH_TOKEN", refresh_token)
    success &= github_service.set_github_secret(
        "X_TARGET_IDS_JSON", '[{type: "dummy", id: "str"}]'
    )
    success &= github_service.set_github_variable("X_CUTOFF_DAYS", cutoff_days)
    success &= github_service.set_github_secret("WEBHOOK_URL", config.WEBHOOK_URL)
    print("X_ACCESS_TOKEN:", access_token)
    if success:
        print("\n✓ Setup completed successfully!")
        print("\nNext steps:")
        print("1. Enable GitHub Actions in your repository")
        print(
            f"2. The workflow will run hourly to delete tweets older than {cutoff_days} days"
        )
    else:
        print("\n✗ Setup completed with errors")
        sys.exit(1)


def main():

    print("=== X (Twitter) OAuth2 PKCE Setup ===")
    print(f"Redirect URI: {config.REDIRECT_URI}")
    print()

    # Mask the client ID
    print(config.X_CLIENT_ID)
    """Main setup function."""
    check_config()

    print("Step 1: Configuration...")
    # Ask for cutoff days
    cutoff_days = input_cutoff_days()

    print("\nStep 2: Opening browser for authentication...")
    auth_url = authorize_url()
    webbrowser.open(auth_url)
    print()

    # Start local server to receive callback and wait
    print("\nStep 3: Starting local server on http://localhost:8080...")
    servers.start_and_wait()
    check_auth_code()

    # Exchange code for tokens
    print("\nStep 4: Exchanging code for tokens...")
    try:
        token_data = twitter_service.exchange_code_for_token(setup_state.auth_code)
        access_token = token_data.get("access_token")
        refresh_token = token_data.get("refresh_token")
        twitter_service.check_tokens(access_token, refresh_token)
        app_state.set_access_token(access_token)
    except Exception as e:
        print(f"Error exchanging code for tokens: {e}")
        sys.exit(1)

    print("\nStep 5: Retrieving user ID...")
    try:
        user_info = twitter_service.get_my_info()
        user_id = user_info.data.id
        print(f"User ID: {user_id}")
    except Exception as e:
        print(f"Error retrieving user ID: {e}")
        sys.exit(1)

    print("\nStep 6: Setting GitHub secrets...")
    save_secrets(user_id, access_token, refresh_token, cutoff_days)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nSetup interrupted by user. Exiting...")
        sys.exit(0)
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        if "--debug" in sys.argv:
            import traceback

            traceback.print_exc()
        sys.exit(1)
