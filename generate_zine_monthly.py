# generate_zine_monthly.py

import os
import json
import subprocess
from datetime import datetime

LOG_PATH = "logs/post_archive.json"
OUT_DIR = "zine_monthly"

def load_monthly_posts(year, month):
    if not os.path.exists(LOG_PATH):
        print("⚠️ 投稿ログが存在しません")
        return []

    with open(LOG_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    selected = []
    for post in data:
        try:
            t = datetime.fromisoformat(post["timestamp"])
            if t.year == year and t.month == month and post["kz_score"] >= 91:
                selected.append((t, post))
        except Exception:
            continue

    return sorted(selected, key=lambda x: x[0])

def format_entry(date, post):
    dt = date.strftime("%Y-%m-%d")
    return f"""### 🕊 {dt}

> {post['text']}

`{post['tags'][0]}` `{post['tags'][1]}`

---
"""

def generate_zine_text(year, month, posts):
    title = f"# ZINE Vol.{month}｜喋らなかった廃墟たち（{year}年{month}月号）"
    intro = "ババァが喋った記録だけを、意味のないまま封じ込めました。\n\n---\n"
    body = "\n".join([format_entry(d, p) for d, p in posts])
    return f"{title}\n\n{intro}{body}"

def export_formats(md_path, base_name):
    subprocess.run(["pandoc", md_path, "-o", f"{base_name}.pdf"])
    subprocess.run(["pandoc", md_path, "-o", f"{base_name}.epub"])

def main():
    now = datetime.now()
    year, month = now.year, now.month
    posts = load_monthly_posts(year, month)

    if not posts:
        print("❌ 今月の収録対象がありません")
        return

    os.makedirs(OUT_DIR, exist_ok=True)
    base_name = os.path.join(OUT_DIR, f"{year}-{month:02d}-zine")
    md_path = base_name + ".md"

    zine_text = generate_zine_text(year, month, posts)

    with open(md_path, "w", encoding="utf-8") as f:
        f.write(zine_text)

    export_formats(md_path, base_name)

    print(f"✅ ZINE出力完了：{md_path}, .pdf, .epub")

if __name__ == "__main__":
    main()
