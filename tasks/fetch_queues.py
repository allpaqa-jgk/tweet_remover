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
    utils.debug_print(all_tweets, "Currently cached tweet IDs")

    # return cached if we have more than NUM_TO_FETCH(100) tweets
    if len(all_tweets) > app_config.NUM_TO_FETCH:
        return

    # Fetch tweets from Twitter API if not enough cached
    print("Fetching tweets from Twitter API...")
    response = twitter_service.get_my_tweets()

    if response.data is not None and len(response.data) > 0:
        for tweet in response.data:
            referenced_tweets = tweet.get("referenced_tweets", [])
            utils.debug_print(tweet, "Processing fetched tweet")
            utils.debug_print(referenced_tweets, "Referenced tweets")
            if (
                referenced_tweets
                and len(referenced_tweets) > 0
                and referenced_tweets[0].type == "retweeted"
            ):
                all_tweets.append({"type": "retweet", "id": tweet["id"]})
            else:
                all_tweets.append({"type": "tweet", "id": tweet["id"]})
    else:
        print("No new tweets found from Twitter API.")

    utils.debug_print(all_tweets, "All tweet IDs after fetching")
    utils.set_tweet_ids(all_tweets)
