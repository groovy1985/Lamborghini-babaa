import os
from datetime import datetime
from utils.validate_post import is_valid_post

WEEKLY_DIR = "note_weekly"
MONTHLY_DIR = "zine_monthly"

def extract_valid_blocks(markdown_text):
    """週報Markdownから `> ` 部分を抽出し、KZHXに通るものだけ返す"""
    blocks = markdown_text.strip().split("\n---\n")
    valid = []

    for block in blocks:
        if "> " not in block:
            continue
        quote_lines = [line.strip()[2:] for line in block.splitlines() if line.strip().startswith("> ")]
        if not quote_lines:
            continue
        text = "\n".join(quote_lines)
        if is_valid_post(text):
            valid.append(block.strip())

    return valid

def integrate_weekly_posts():
    now = datetime.now()
    fname = f"{now.year}-{now.month:02d}-zine.md"
    monthly_path = os.path.join(MONTHLY_DIR, fname)

    with open(monthly_path, "a", encoding="utf-8") as zine:
        zine.write("\n## 🗓️ Weekly Highlights（KZHX-L4.1 準拠）\n\n")

        for fname in sorted(os.listdir(WEEKLY_DIR)):
            if not fname.endswith(".md"):
                continue

            path = os.path.join(WEEKLY_DIR, fname)
            with open(path, encoding="utf-8") as f:
                content = f.read()

            valid_blocks = extract_valid_blocks(content)
            if valid_blocks:
                zine.write(f"### 📅 {fname.replace('.md', '')}\n\n")
                for block in valid_blocks:
                    zine.write(block + "\n\n")

    print(f"✅ 統合完了：{monthly_path}")

if __name__ == "__main__":
    integrate_weekly_posts()
