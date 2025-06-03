import os
import sys
import tweepy
from dotenv import load_dotenv
from post_generator import generate_babaa_post

# ✅ 相対パスから utils を読み込めるようにする
sys.path.append(os.path.abspath(os.path.dirname(__file__)))
from utils.post_logger import log_post  # ← ログ記録関数の読み込み

# ✅ 環境変数の読み込み
load_dotenv()

# ✅ 環境変数の取得関数
def get_env(name):
    value = os.getenv(name)
    if not value:
        raise ValueError(f"❌ 環境変数 {name} が設定されていません")
    return value

# ✅ 投稿生成
try:
    post = generate_babaa_post()
except Exception as e:
    print(f"❌ ポスト生成エラー: {e}")
    exit(1)

# ✅ 投稿処理（API v2: create_tweet使用）
if post and "text" in post:
    try:
        print(f"🕊️ 投稿中: {post['text']}")

        client = tweepy.Client(
            consumer_key=get_env("TWITTER_API_KEY"),
            consumer_secret=get_env("TWITTER_API_SECRET"),
            access_token=get_env("TWITTER_ACCESS_TOKEN"),
            access_token_secret=get_env("TWITTER_ACCESS_SECRET"),
            bearer_token=get_env("TWITTER_BEARER_TOKEN")
        )

        response = client.create_tweet(text=post['text'])
        print(f"✅ 投稿完了: https://twitter.com/user/status/{response.data['id']}")

        # ✅ 投稿成功時のみログを保存
        log_post(
            text=post["text"],
            tags=post.get("tags", ["未知", "分類不可"]),
            kz_score=post.get("kz_score", 90.0)
        )

    except Exception as e:
        print(f"❌ 投稿失敗: {e}")
else:
    print("🚫 投稿するポストが生成されませんでした")
