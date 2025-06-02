import os
import tweepy
from dotenv import load_dotenv
from post_generator import generate_babaa_post

# ✅ 環境変数の読み込み
load_dotenv()

# ✅ OAuth1.0a認証
try:
    auth = tweepy.OAuth1UserHandler(
        os.getenv("TWITTER_API_KEY"),
        os.getenv("TWITTER_API_SECRET"),
        os.getenv("TWITTER_ACCESS_TOKEN"),
        os.getenv("TWITTER_ACCESS_SECRET")
    )
    api = tweepy.API(auth)
except Exception as e:
    print(f"❌ 認証情報の初期化に失敗: {e}")
    exit(1)

# ✅ 認証確認
try:
    if not api.verify_credentials():
        print("❌ 認証エラー：APIキーまたはトークンが無効です")
        exit(1)
    else:
        print("✅ 認証成功：トークンは有効です")
except Exception as e:
    print(f"❌ 認証チェック失敗: {e}")
    exit(1)

# ✅ 1件だけ生成・投稿
try:
    post = generate_babaa_post()
except Exception as e:
    print(f"❌ ポスト生成エラー: {e}")
    exit(1)

if post and "text" in post:
    try:
        print(f"🕊️ 投稿中: {post['text']}")
        api.update_status(status=post['text'])  # API v1.1 経由の投稿
        print("✅ 投稿完了")
    except Exception as e:
        print(f"❌ 投稿失敗: {e}")
else:
    print("🚫 投稿するポストが生成されませんでした")
