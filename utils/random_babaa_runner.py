import sys
import os

# repoルートをimportパスに追加
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import tweepy
import random
import re
from reply_generator import generate_babaa_reply  # ← post_generatorではなくreply_generatorを使う

TARGET_ACCOUNTS = [
    "YahooNewsTopics",
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
        user = client.get_user(username=account).data
        tweets = client.get_users_tweets(
            user.id,
            max_results=5,
            tweet_fields=["created_at"]
        ).data or []

        count = 0
        random.shuffle(tweets)  # 各回ランダム化

        for tweet in tweets:
            if count >= 1:  # 各アカウントで1件だけ投稿
                break
            if is_earthquake_related(tweet.text):
                continue

            result = generate_babaa_reply(tweet.text)  # ←元ツイート本文を渡す
            if result is None:
                print(f"[WARN] Babaa post generation skipped due to daily limit or failure.")
                continue

            reply_text = f"@{account} {result['text']}"
            print(f"[POST] @{account} → {reply_text}")

            try:
                client.create_tweet(
                    text=reply_text,
                    in_reply_to_tweet_id=tweet.id  # 正しいリプライパラメータ
                )
                count += 1
            except Exception as e:
                print(f"[ERROR] Failed to post reply: {e}")

if __name__ == "__main__":
    print("[INFO] Executing babaa reply bomb (context-aware).")
    main()
