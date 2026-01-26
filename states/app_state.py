from configs.app_config import X_ACCESS_TOKEN

access_token = X_ACCESS_TOKEN


def get_access_token():
    return access_token


def set_access_token(token: str):
    global access_token
    access_token = token
