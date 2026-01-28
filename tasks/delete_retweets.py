# Remove retweets older than a certain number of days


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
            response = twitter_service.delete_my_retweet(tweet["id"])
            if "status_code" in response and response.status_code == 200:
                print(f"Deleted retweet ID {tweet['id']}")
                num_deleted += 1
                removed_ids.add(tweet["id"])
            else:
                print(
                    f"Error deleting retweet ID {tweet['id']}: {response.status_code} {response.text}"
                )

        if num_deleted >= app_config.REMOVE_RETWEETS_BATCH_SIZE:  # 1
            break
    for removed_id in removed_ids:
        all_tweets = [t for t in all_tweets if t["id"] != removed_id]

    utils.set_tweet_ids(all_tweets)
    print(f"Total retweets deleted: {num_deleted}")
