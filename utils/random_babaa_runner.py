import sys
import os

# repoルートをimportパスに追加
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import tweepy
import random
import re
from reply_generator import generate_babaa_reply

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
        try:
            user = client.get_user(username=account).data
            tweets = client.get_users_tweets(
                user.id,
                max_results=5,  # APIの仕様上5以上必須
                tweet_fields=["created_at"]
            ).data or []

            # 取得後は先頭1件のみ処理してAPI負荷を最小化
            tweets = tweets[:1]

            for tweet in tweets:
                if is_earthquake_related(tweet.text):
                    continue

                result = generate_babaa_reply(tweet.text)
                if result is None:
                    print(f"[WARN] Babaa post generation skipped due to daily limit or failure.")
                    continue

                reply_text = f"@{account} {result['text']}"
                print(f"[POST] @{account} → {reply_text}")

                try:
                    client.create_tweet(
                        text=reply_text,
                        in_reply_to_tweet_id=tweet.id
                    )
                except Exception as e:
                    print(f"[ERROR] Failed to post reply: {e}")

        except tweepy.errors.TooManyRequests as e:
            print("[ERROR] API rate limit reached, skipping remaining accounts for today.")
            break
        except Exception as e:
            print(f"[ERROR] Unexpected error: {e}")

if __name__ == "__main__":
    print("[INFO] Executing babaa reply bomb (context-aware, minimized API calls).")
    main()
