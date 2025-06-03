import os
from utils.validate_post import is_valid_post

WEEKLY_DIR = "note_weekly"
MONTHLY_PATH = "zine_monthly/monthly_zine.md"

def integrate_weekly_posts():
    with open(MONTHLY_PATH, "a", encoding="utf-8") as zine:
        zine.write("\n## 🗓️ Weekly Highlights（KZHX-L4.1 準拠）\n\n")
        for fname in sorted(os.listdir(WEEKLY_DIR)):
            if not fname.endswith(".md"):
                continue

            path = os.path.join(WEEKLY_DIR, fname)
            with open(path, encoding="utf-8") as f:
                content = f.read().strip()

            if is_valid_post(content):
                zine.write(f"### {fname.replace('.md','')}\n")
                zine.write(content + "\n\n")

if __name__ == "__main__":
    integrate_weekly_posts()
