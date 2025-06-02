import os
import tweepy
from dotenv import load_dotenv
from post_generator import generate_babaa_post

# ✅ 環境変数の読み込み
load_dotenv()

# 🔐 各種認証情報の取得
API_KEY = os.getenv("TWITTER_API_KEY")
API_SECRET = os.getenv("TWITTER_API_SECRET")
ACCESS_TOKEN = os.getenv("TWITTER_ACCESS_TOKEN")
ACCESS_SECRET = os.getenv("TWITTER_ACCESS_SECRET")
BEARER_TOKEN = os.getenv("TWITTER_BEARER_TOKEN")

# ✅ OAuth1.0a 認証（User認証：投稿用）
try:
    auth = tweepy.OAuth1UserHandler(API_KEY, API_SECRET, ACCESS_TOKEN, ACCESS_SECRET)
    api = tweepy.API(auth)
    if not api.verify_credentials():
        print("❌ OAuth認証失敗：トークンが無効です")
        exit(1)
    print("✅ OAuth認証成功：ユーザー認証OK")
except Exception as e:
    print(f"❌ OAuth認証エラー: {e}")
    exit(1)

# ✅ tweepy.Client（App認証：必要に応じて利用）
try:
    client = tweepy.Client(
        bearer_token=BEARER_TOKEN,
        consumer_key=API_KEY,
        consumer_secret=API_SECRET,
        access_token=ACCESS_TOKEN,
        access_token_secret=ACCESS_SECRET
    )
