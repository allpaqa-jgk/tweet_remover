import tasks.fetch_queues as fetch_queues
import tasks.delete_tweets as delete_tweets

import utils.common as utils


def main():
    fetch_queues.do()
    delete_tweets.do()


if __name__ == "__main__":
    utils.exec_with_discord_notification(main)
