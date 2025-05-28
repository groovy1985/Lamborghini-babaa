import random
import json
import os
from datetime import datetime
import openai  # ← こちらでOK

from utils.validate_post import is_valid_post
from utils.format_utils import trim_text

# APIキー設定
openai.api_key = os.getenv("OPENAI_API_KEY")

base_dir = os.path.dirname(os.path.abspath(__file__))
style_path = os.path.join(base_dir, "babaa_styles.json")
STYLE_USAGE_PATH = os.path.join(base_dir, "logs/style_usage.json")

with open(style_path, "r", encoding="utf-8") as f:
    styles = json.load(f)

def get_unused_styles():
    used_ids = set()
    if os.path.exists(STYLE_USAGE_PATH):
        try:
            with open(STYLE_USAGE_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, list):
                    used_ids = set(data)
                else:
                    print("⚠️ style_usage.json の内容が不正です（list ではありません）")
        except Exception as e:
            print(f"⚠️ style_usage.json 読み込みエラー: {e}")
            used_ids = set()
    return [style for style in styles if style["id"] not in used_ids]

def mark_style_used(style_id):
    used = []
    if os.path.exists(STYLE_USAGE_PATH):
        with open(STYLE_USAGE_PATH, "r", encoding="utf-8") as f:
            try:
                loaded = json.load(f)
                if isinstance(loaded, list):
                    used = loaded
                elif isinstance(loaded, dict):
                    used = list(loaded.values())
            except Exception as e:
                print(f"⚠️ style_usage.json 読み込みエラー: {e}")
    used.append(style_id)
    with open(STYLE_USAGE_PATH, "w", encoding="utf-8") as f:
        json.dump(used, f, ensure_ascii=False, indent=2)

def apply_style_to_generate_text(style, seed):
    prompt = f"""
あなたは高齢女性の人格を持つポエム生成機です。
以下のスタイルに従い、再構成不可能な構文崩壊系ポストを生成してください。

スタイル: {style['label']}（{style['structure']}）
特徴: {style['notes']}

条件:
- 140文字以内
- 再構成・要約・感想を拒否
- 明確な意味を避ける
- キーワード: {seed}
"""
    try:
        response = openai.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "あなたはババァ風ポエム構文破壊AIです"},
                {"role": "user", "content": prompt.strip()}
            ],
            temperature=1.2,
            max_tokens=160
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"OpenAI error: {e}")
        return None

def generate_babaa_post():
    unused_styles = get_unused_styles()
    if not unused_styles:
        print("⚠️ 使用可能なスタイルが残っていません")
        return None

    random.shuffle(unused_styles)
    for style in unused_styles:
        seed = random.choice(["粉", "鹿", "黙り", "パウダー", "遺言", "昼寝", "冷蔵庫", "軋み", "カーテン"])
        print(f"🔁 スタイル: {style['label']}｜キーワード: {seed}")
        post = apply_style_to_generate_text(style, seed)

        if post:
            print(f"📝 生成内容:\n{post}\n")

        if post and is_valid_post(post):
            post = trim_text(post)
            mark_style_used(style["id"])
            return {
                "text": post,
                "tags": [f"#{style['label']}", "#構文爆撃ババァ"],
                "style_id": style["id"],
                "timestamp": datetime.now().isoformat()
            }
        else:
            print("❌ 投稿冷却／生成失敗")

    return None
