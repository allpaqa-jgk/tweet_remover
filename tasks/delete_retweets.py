# Remove retweets older than a certain number of days


import tweepy
import utils.common as utils
import configs.app_config as app_config
import services.twitter as twitter_service


# Delete retweets based on fetched queues
def do() -> None:
    print("Deleting retweets from fetched queues...")

    all_tweets = utils.get_tweet_ids()
    if not all_tweets or len(all_tweets) == 0:
        print("No retweets to delete.")
        return

    num_deleted = 0
    removed_ids = set()
    for tweet in all_tweets:
        if tweet["type"] == "retweet":
            try:
                twitter_service.delete_my_retweet(tweet["id"])
                print(f"Deleted retweet ID {tweet['id']}")
                num_deleted += 1
                removed_ids.add(tweet["id"])
            except tweepy.TweepyException as e:
                print(f"Error deleting retweet ID {tweet['id']}: {e}")

            if num_deleted >= app_config.REMOVE_RETWEETS_BATCH_SIZE:
                break
    for removed_id in removed_ids:
        all_tweets = [t for t in all_tweets if t["id"] != removed_id]

    utils.set_tweet_ids(all_tweets)
    print(f"Total retweets deleted: {num_deleted}")
