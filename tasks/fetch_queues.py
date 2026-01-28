# Fetch Tweets older than a certain number of days

import tweepy
import utils.common as utils
import configs.app_config as app_config
import services.twitter as twitter_service


# get cached tweets and new targets older than cutoff days
# API Rate limit: 1 requests / 15 mins PER USER
# Return [{type: "tweet"/"retweet", id: str}, ...] from Github Secrets or X API
def do() -> None:
    print("Fetching tweets for retweet deletion task...")

    all_tweets = utils.get_tweet_ids()

    # return cached if we have more than NUM_TO_FETCH(100) tweets
    if len(all_tweets) > app_config.NUM_TO_FETCH:
        return

    # Fetch tweets from Twitter API if not enough cached
    print("Fetching tweets from Twitter API...")
    response = twitter_service.get_my_tweets()
    utils.debug_print(response, "Twitter API response for fetching tweets")

    if "data" in response:
        for tweet in response["data"]:
            if (
                tweet.get("referenced_tweets")
                and len(tweet["referenced_tweets"]) > 0
                and tweet["referenced_tweets"][0]["type"] == "retweeted"
            ):
                all_tweets.append({"type": "retweet", "id": tweet["id"]})
            else:
                all_tweets.append({"type": "tweet", "id": tweet["id"]})

    utils.set_tweet_ids(all_tweets)
