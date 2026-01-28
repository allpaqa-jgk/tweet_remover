import json
from configs.app_config import X_ACCESS_TOKEN, X_TARGET_IDS_JSON
from utils.common import TweetInfo


# Schema: [{type: "tweet"/"retweet", id: str}, ...]
def init_tweets() -> list[TweetInfo]:
    _tweets = []

    for t in json.loads(X_TARGET_IDS_JSON):
        type = t.get("type")
        id = t.get("id")
        if type in ["tweet", "retweet"] and id:
            _tweets.append({"type": type, "id": id})

    return _tweets


access_token = X_ACCESS_TOKEN
tweets = init_tweets()


def get_access_token() -> str:
    return access_token


def set_access_token(token: str) -> None:
    global access_token
    access_token = token


# Get X_TWEET_IDS [{type: "tweet"/"retweet", id: str}, ...]
def get_tweets() -> list[TweetInfo]:
    return tweets


# Set X_TWEET_IDS [{type: "tweet"/"retweet", id: str}, ...]
def set_tweets(_tweets: list[TweetInfo]) -> None:
    global tweets

    tweets = _tweets
