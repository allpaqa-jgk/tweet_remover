# Delete Tweets older than a certain number of days


import utils.common as utils
import configs.app_config as app_config
import states.app_state as app_state
import services.twitter as twitter_service


# Remove tweets from authenticated user(Retweets are handled on another task)
# API Rate limit: 17 requests / 24 hours PER USER
#                 17 requests / 24 hours PER APP
# Delete tweets based on fetched queues
def do():
    print("Deleting tweets from fetched queues...")

    all_tweets = app_state.get_tweets()
    if not all_tweets or len(all_tweets) == 0:
        print("No tweets to delete.")
        return

    num_deleted = 0
    removed_ids = set()
    for tweet in all_tweets:
        if tweet["type"] == "tweet":
            response = twitter_service.delete_my_tweet(tweet["id"])
            if response.status_code == 200:
                print(f"Deleted tweet ID {tweet['id']}")
                num_deleted += 1
                removed_ids.add(tweet["id"])
            else:
                print(
                    f"Error deleting tweet ID {tweet['id']}: {response.status_code} {response.text}"
                )

        if num_deleted >= app_config.REMOVE_TWEETS_BATCH_SIZE:
            break
    for removed_id in removed_ids:
        all_tweets = [t for t in all_tweets if t["id"] != removed_id]

    utils.set_tweet_ids(all_tweets)
    print(f"Total tweets deleted: {num_deleted}")
