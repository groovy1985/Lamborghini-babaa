import random
import sys
import tweepy
import os
import re
from post_generator import generate_babaa_post

TARGET_ACCOUNTS = [
    "YahooNewsTopics",
    "YahooTopicsEdit",
    "nhk_news"
]

EARTHQUAKE_KEYWORDS = [
    "地震", "震度", "震源", "津波", "マグニチュード"
]

def is_earthquake_related(text):
    return any(kw in text for kw in EARTHQUAKE_KEYWORDS)

def main():
    client = tweepy.Client(
        bearer_token=os.environ["TWITTER_BEARER_TOKEN"],
        consumer_key=os.environ["TWITTER_API_KEY"],
        consumer_secret=os.environ["TWITTER_API_SECRET"],
        access_token=os.environ["TWITTER_ACCESS_TOKEN"],
        access_token_secret=os.environ["TWITTER_ACCESS_SECRET"]
    )

    for account in TARGET_ACCOUNTS:
        # 直近10件取得
        user = client.get_user(username=account).data
        tweets = client.get_users_tweets(
            user.id,
            max_results=10,
            tweet_fields=["created_at"]
        ).data or []

        count = 0
        random.shuffle(tweets)  # 各回ランダム化

        for tweet in tweets:
            if count >= 2:
                break
            if is_earthquake_related(tweet.text):
                continue

            reply_text = generate_babaa_post(tweet.text)
            print(f"[POST] @{account} → {reply_text}")

            try:
                client.create_tweet(
                    text=reply_text,
                    reply={"in_reply_to_tweet_id": tweet.id}
                )
                count += 1
            except Exception as e:
                print(f"[ERROR] Failed to post reply: {e}")

if __name__ == "__main__":
    # ランダムで40%の確率で実行
    if random.random() < 0.4:
        print("[INFO] Selected: executing babaa reply bomb.")
        main()
    else:
        print("[INFO] Skipped: not executing this time.")
        sys.exit(0)
