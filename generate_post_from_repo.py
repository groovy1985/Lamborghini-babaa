import os
import sys
from datetime import datetime

# ✅ 外部モジュールの読み込み（ババァ用に差し替え）
from generate_post_lastwords import generate_babaa_post
from validate_post import is_valid_post
from tweet_with_token import tweet_post
from phrase_store import load_used_phrases, save_phrase

# ✅ 対応リポジトリ（今回は Last-Words 専用でも拡張性保持）
SUPPORTED_REPOS = {
    "last-words": "output/last_words"
}

# ✅ 最新ファイルからテキスト取得
def get_latest_text(poems_dir):
    if not os.path.exists(poems_dir):
        os.makedirs(poems_dir, exist_ok=True)
        raise FileNotFoundError(f"❌ Directory created but empty: {poems_dir}")

    files = sorted(
        [f for f in os.listdir(poems_dir) if f.endswith(".md")],
        key=lambda x: os.path.getmtime(os.path.join(poems_dir, x))
    )
    if not files:
        raise FileNotFoundError(f"❌ No .md files found in {poems_dir}/")

    latest_file = files[-1]
    full_path = os.path.join(poems_dir, latest_file)
    with open(full_path, "r", encoding="utf-8") as f:
        text = f.read()

    print(f"📘 Loaded: {latest_file}")
    return text.strip(), latest_file

# ✅ ログ記録
def log_post(post, repo):
    try:
        os.makedirs("output/logs", exist_ok=True)
        with open("output/logs/post_log.txt", "a", encoding="utf-8") as log:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            log.write(f"[{timestamp}] ({repo}) {post}\n")
    except Exception as e:
        print(f"⚠️ Logging failed: {e}")

# ✅ メイン処理
def main():
    if len(sys.argv) < 3:
        print("Usage: python generate_post_from_repo.py [repo] [trigger]")
        sys.exit(1)

    repo = sys.argv[1]
    poems_dir = SUPPORTED_REPOS.get(repo)

    if not poems_dir:
        print(f"❌ Unsupported repo: {repo}")
        sys.exit(1)

    try:
        source_text, filename = get_latest_text(poems_dir)

        # ✅ ババァ会話構文の生成（ソースは一応渡せるが無視し
