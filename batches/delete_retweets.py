import tasks.delete_retweets as delete_retweets

import utils.common as utils


def main():
    delete_retweets.do()


if __name__ == "__main__":
    utils.exec_with_discord_notification(main)
