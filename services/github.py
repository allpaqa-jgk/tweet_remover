import json
import subprocess


def get_github_auth_status() -> bool:
    """Check if gh CLI is authenticated."""
    try:
        subprocess.run(
            ["gh", "auth", "status"],
            capture_output=True,
            text=True,
            check=True,
        )
        print("✓ gh CLI is authenticated")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ gh CLI authentication failed: {e.stderr}")
        return False


def set_github_secret(secret_name: str, secret_value: str) -> bool:
    """Set a GitHub secret using gh CLI."""
    try:
        # Use gh CLI to set the secret
        subprocess.run(
            ["gh", "secret", "set", secret_name, "-b", secret_value],
            capture_output=True,
            text=True,
            check=True,
        )
        print(f"✓ Secret {secret_name} set successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Failed to set secret {secret_name}: {e.stderr}")
        raise e


def set_github_variable(var_name: str, var_value: str) -> bool:
    """Set a GitHub variable using gh CLI."""
    try:
        print(f"Setting variable {var_name}: {var_value}")
        # Use gh CLI to set the variable
        subprocess.run(
            ["gh", "variable", "set", var_name, "-b", var_value],
            capture_output=True,
            text=True,
            check=True,
        )
        print(f"✓ Variable {var_name} set successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Failed to set variable {var_name}: {e.stderr}")
        raise e


def save_target_ids(ids: list) -> bool:  # [{type: "tweet"/"retweet", id: str}, ...]
    # リストを JSON 文字列にして Secret に保存
    try:
        json_str = json.dumps(ids)
        subprocess.run(
            ["gh", "secret", "set", "X_TARGET_IDS_JSON", "--body", json_str],
            capture_output=True,
            text=True,
            check=True,
        )
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Failed to save target IDs: {e.stderr}")
        raise e
