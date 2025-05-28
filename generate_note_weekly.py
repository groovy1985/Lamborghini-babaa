# generate_note_weekly.py

import os
import json
from datetime import datetime, timedelta

LOG_PATH = "logs/post_archive.json"
OUT_DIR = "note_weekly"

def load_recent_posts(days=7):
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
            if t >= cutoff:
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

def generate_weekly_note():
    posts = load_recent_posts()
    if not posts:
        print("❌ 今週の投稿がありません")
        return

    out = "# 🧓 Lamborghini-babaa Weekly Note\n\n"
    out += "※ 今週喋ったババァたちの記録（意味はない）\n\n"

    for date, post in posts:
        out += format_post(date, post)

    os.makedirs(OUT_DIR, exist_ok=True)
    out_path = os.path.join(OUT_DIR, f"{datetime.now().strftime('%Y-%m-%d')}-note.md")

    with open(out_path, "w", encoding="utf-8") as f:
        f.write(out)

    print(f"✅ 週報を出力しました：{out_path}")

if __name__ == "__main__":
    generate_weekly_note()
