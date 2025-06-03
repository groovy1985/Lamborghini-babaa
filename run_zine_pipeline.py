import os
import json
import argparse
import yaml
import subprocess
from datetime import datetime, timedelta
from utils.validate_post import is_valid_post

LOG_PATH = "logs/post_archive.json"
NOTE_DIR = "note_weekly"
ZINE_DIR = "zine_monthly"

# 週次ノート用
def load_recent_valid_posts(days=7):
    with open(LOG_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    cutoff = datetime.now() - timedelta(days=days)
    posts = []

    for post in data:
        try:
            t = datetime.fromisoformat(post["timestamp"])
            if t >= cutoff and is_valid_post(post["text"]):
                posts.append((t, post))
        except Exception:
            continue

    return sorted(posts, key=lambda x: x[0])

def generate_weekly_note():
    posts = load_recent_valid_posts()
    if not posts:
        print("❌ 今週の有効な投稿がありません（KZHX非準拠）")
        return

    now = datetime.now()
    year, week = now.year, now.isocalendar()[1]
    fname = f"{year}-W{week:02d}-note"
    md_path = os.path.join(NOTE_DIR, f"{fname}.md")
    yaml_path = os.path.join(NOTE_DIR, f"{fname}.yaml")

    os.makedirs(NOTE_DIR, exist_ok=True)

    md_out = "# 🧓 Lamborghini-babaa Weekly Note\n\n"
    md_out += "※ 今週喋ったババァたちの記録（KZHX準拠のみ）\n\n"
    md_out += "\n".join([
        f"""### 🗓 {d.strftime("%Y-%m-%d")}\n\n> {p['text']}\n\n`{p['tags'][0]}` `{p['tags'][1]}`\n\n---\n"""
        for d, p in posts
    ])

    with open(md_path, "w", encoding="utf-8") as f:
        f.write(md_out)

    yaml_data = {
        "title": f"Weekly Note W{week} ({year})",
        "generated_at": now.isoformat(),
        "posts": [
            {"date": d.strftime("%Y-%m-%d"), "tags": p["tags"], "text": p["text"]}
            for d, p in posts
        ]
    }
    with open(yaml_path, "w", encoding="utf-8") as f:
        yaml.dump(yaml_data, f, allow_unicode=True, sort_keys=False)

    print(f"✅ WEEKLY NOTE 完成：{md_path}")
    git_commit(md_path)
    git_commit(yaml_path)

# 月次ZINE用
def load_monthly_posts(year, month):
    with open(LOG_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    return sorted([
        (datetime.fromisoformat(p["timestamp"]), p)
        for p in data
        if datetime.fromisoformat(p["timestamp"]).year == year
        and datetime.fromisoformat(p["timestamp"]).month == month
        and p.get("kz_score", 0) >= 91
    ], key=lambda x: x[0])

def extract_weekly_highlights():
    results = []
    for fname in sorted(os.listdir(NOTE_DIR)):
        if not fname.endswith(".md"):
            continue
        path = os.path.join(NOTE_DIR, fname)
        with open(path, encoding="utf-8") as f:
            content = f.read().strip()
        if is_valid_post(content):
            results.append((fname, content))
    return results

def generate_monthly_zine():
    now = datetime.now()
    year, month = now.year, now.month
    fname = f"{year}-{month:02d}-zine"
    md_path = os.path.join(ZINE_DIR, f"{fname}.md")
    yaml_path = os.path.join(ZINE_DIR, f"{fname}.yaml")
    os.makedirs(ZINE_DIR, exist_ok=True)

    posts = load_monthly_posts(year, month)
    if not posts:
        print("❌ 今月の収録対象がありません")
        return

    title = f"# ZINE Vol.{month}｜喋らなかった廃墟たち（{year}年{month}月号）"
    intro = "ババァが喋った記録だけを、意味のないまま封じ込めました。\n\n---\n"

    md_body = "\n".join([
        f"""### 🕊 {d.strftime("%Y-%m-%d")}\n\n> {p["text"]}\n\n`{p["tags"][0]}` `{p["tags"][1]}`\n\n---\n"""
        for d, p in posts
    ])

    highlights = extract_weekly_highlights()
    if highlights:
        md_body += "\n## 🗓️ Weekly Highlights（KZHX-L4.1 準拠）\n\n"
        for fname, content in highlights:
            md_body += f"### 📅 {fname.replace('.md', '')}\n\n{content}\n\n"

    with open(md_path, "w", encoding="utf-8") as f:
        f.write(f"{title}\n\n{intro}{md_body}")

    yaml_data = {
        "title": f"ZINE Vol.{month}｜喋らなかった廃墟たち（{year}年{month}月号）",
        "intro": intro.strip(),
        "generated_at": now.isoformat(),
        "posts": [
            {"date": d.strftime("%Y-%m-%d"), "tags": p["tags"], "text": p["text"]}
            for d, p in posts
        ],
        "weekly_highlights": [
            {"source": fname.replace(".md", ""), "content": content}
            for fname, content in highlights
        ]
    }
    with open(yaml_path, "w", encoding="utf-8") as f:
        yaml.dump(yaml_data, f, allow_unicode=True, sort_keys=False)

    print(f"✅ MONTHLY ZINE 完成：{md_path}")
    git_commit(md_path)
    git_commit(yaml_path)

# 共通：Git commit
def git_commit(path):
    subprocess.run(["git", "add", path])
    subprocess.run(["git", "commit", "-m", f"Auto: update {os.path.basename(path)}"], check=False)

# CLIエントリーポイント
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["weekly", "monthly"], required=True)
    args = parser.parse_args()

    if args.mode == "weekly":
        generate_weekly_note()
    elif args.mode == "monthly":
        generate_monthly_zine()
