# post_generator.py

import random
from datetime import datetime
from styles.babaa_styles import get_random_style
from tag_generator import generate_tags
from evaluate_kz import evaluate_kz
from utils.validate_post import is_valid_post
import json
import os

MAX_LENGTH = 140

def generate_babaa_post():
    style = get_random_style()
    seed = random.randint(100000, 999999)

    # スタイルに基づいて喋り生成（プレースホルダ）
    post = apply_style_to_generate_text(style, seed)

    if len(post) > MAX_LENGTH or not is_valid_post(post):
        return None  # 冷却対象

    tags = generate_tags(post)
    kz_score = evaluate_kz(post)

    if kz_score < 91:
        return None  # 冷却対象

    result = {
        "text": post,
        "tags": tags,
        "kz_score": kz_score,
        "timestamp": datetime.now().isoformat(),
        "style_id": style["style_id"]
    }

    save_post(result)
    return result


def apply_style_to_generate_text(style, seed):
    """スタイルに応じた喋り生成（仮実装）"""
    random.seed(seed)
    if style["style_id"] == "BA-0042":  # 呼びかけ逸脱型
        a = random.choice(["ねえ、起きてる？", "さっきの話、まだ続いてる？"])
        b = random.choice(["でも冷蔵庫が怒ってたのよ", "だけど雨って名前だったでしょ"])
        return f"{a}\n{b}"
    else:
        return f"昔の夢がまだ乾いてないのよねぇ。昨日の指輪が冷蔵庫にいたし。"


def save_post(post_data):
    archive_path = "logs/post_archive.json"
    os.makedirs("logs", exist_ok=True)

    if os.path.exists(archive_path):
        with open(archive_path, "r", encoding="utf-8") as f:
            archive = json.load(f)
    else:
        archive = []

    archive.append(post_data)

    with open(archive_path, "w", encoding="utf-8") as f:
        json.dump(archive, f, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    result = generate_babaa_post()
    if result:
        print("✅ Generated post:")
        print(result["text"])
        print("Tags:", " ".join(result["tags"]))
    else:
        print("❌ 冷却：投稿基準未達")
