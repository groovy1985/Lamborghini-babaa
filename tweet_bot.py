import os
import sys
import tweepy
from dotenv import load_dotenv
from post_generator import generate_babaa_post

# ✅ 相対パスから shared_core を読み込めるようにする
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

# ✅ Syntaxtemple保存関数の読み込み
from shared_core.file_writer import save_raw_post

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

        # ✅ 構文国家 raw_post 保存（評価前の構文死体）
        save_raw_post("baba", post["text"])

    except Exception as e:
        print(f"❌ 投稿失敗: {e}")
else:
    print("🚫 投稿するポストが生成されませんでした")
