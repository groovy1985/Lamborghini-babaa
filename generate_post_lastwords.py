import sys
import tweet_bot  # ← これだけで投稿まで完了

if __name__ == "__main__":
    repo = sys.argv[1] if len(sys.argv) > 1 else "Last-Words-Archive"
    trigger = sys.argv[2] if len(sys.argv) > 2 else "manual"
    print(f"🧙‍♀️ Triggered by {repo} with event '{trigger}'")
