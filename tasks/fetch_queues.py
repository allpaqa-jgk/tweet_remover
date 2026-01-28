# Fetch Tweets older than a certain number of days

import utils.common as utils
import states.app_state as app_state
import services.twitter as twitter_service


# get cached tweets and new targets older than cutoff days
# API Rate limit: 1 requests / 15 mins PER USER
# Return [{type: "tweet"/"retweet", id: str}, ...] from Github Secrets or X API
def do():
    print("Fetching tweets for retweet deletion task...")

    all_tweets = app_state.get_tweets()

    # return cached if we have more than 100 tweets
    if len(all_tweets) > 100:
        return all_tweets

    # Fetch tweets from Twitter API if not enough cached
    print("Fetching tweets from Twitter API...")
    response = twitter_service.get_my_tweets()
    utils.debug_print(response, "Twitter API response for fetching tweets")
    if response.status_code != 200:
        raise Exception(
            f"Error fetching tweets: {response.status_code} {response.text}"
        )

    data = response.json()
    if "data" in data:
        for tweet in data["data"]:
            if (
                tweet.get("referenced_tweets")
                and tweet["referenced_tweets"][0]["type"] == "retweeted"
            ):
                all_tweets.append({"type": "retweet", "id": tweet["id"]})
            else:
                all_tweets.append({"type": "tweet", "id": tweet["id"]})

    utils.set_tweet_ids(all_tweets)
