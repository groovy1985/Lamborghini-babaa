import os
import json
import subprocess
from datetime import datetime, timedelta
from utils.validate_post import is_valid_post  # KZHX-L4.1検査

LOG_PATH = "logs/post_archive.json"
OUT_DIR = "note_weekly"

def load_recent_valid_posts(days=7):
    if not os.path.exists(LOG_PATH):
        print("⚠️ 投稿ログが存在しません")
        return []

    with open(LOG_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    cutoff = datetime.now() - timedelta(days=days)
    recent = []

    for post in data:
        try:
            t = datetime.fromisoformat(post["timestamp"])
            if t >= cutoff and is_valid_post(post["text"]):
                recent.append((t, post))
        except Exception:
            continue

    return sorted(recent, key=lambda x: x[0])  # 日付順にソート

def format_post(date, post):
    dt = date.strftime("%Y-%m-%d")
    return f"""### 🗓 {dt}

> {post['text']}

`{post['tags'][0]}` `{post['tags'][1]}`

---
"""

def get_week_number_filename():
    now = datetime.now()
    week_num = now.isocalendar()[1]
    return f"{now.year}-W{week_num:02d}-note.md"

def git_commit(path):
    subprocess.run(["git", "add", path])
    subprocess.run(["git", "commit", "-m", f"Add weekly note: {os.path.basename(path)}"])

def generate_weekly_note():
    posts = load_recent_valid_posts()
    i
