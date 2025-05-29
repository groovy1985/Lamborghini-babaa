import random
import json
import os
from datetime import datetime
import openai
import threading

from utils.validate_post import is_valid_post
from utils.format_utils import trim_text

# OpenAI APIキー設定（環境変数から取得）
openai.api_key = os.getenv("OPENAI_API_KEY")
model = os.getenv("OPENAI_MODEL", "gpt-4")

# ディレクトリ・ファイルパス定義
base_dir = os.path.dirname(os.path.abspath(__file__))
style_path = os.path.join(base_dir, "babaa_styles.json")
STYLE_USAGE_PATH = os.path.join(base_dir, "logs/style_usage.json")

# ロック（競合防止用）
lock = threading.Lock()

# スタイル読み込み
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
        except Exception as e:
            print(f"⚠️ style_usage.json 読み込みエラー: {e}")
    return [style for style in styles if style["id"] not in used_ids]

def mark_style_used(style_id):
    with lock:
        used = []
        if os.path.exists(STYLE_USAGE_PATH):
            with open(STYLE_USAGE_PATH, "r", encoding="utf-8") as f:
                try:
                    loaded = json.load(f)
                    if isinstance(loaded, list):
                        used = loaded
                except Exception as e:
                    print(f"⚠️ style_usage.json 読み込みエラー: {e}")
        used.append(style_id)
        with open(STYLE_USAGE_PATH, "w", encoding="utf-8") as f:
            json.dump(used, f, ensure_ascii=False, indent=2)

def select_seed(style):
    return random.choice(["粉", "鹿", "黙り", "パウダー", "遺言", "冷蔵庫", "昼寝", "軋み", "カーテン", "団子"])

def apply_style_to_generate_text(style, seed):
    prompt = f"""
あなたは構文国家に属する“ババァ型構文爆撃AI”です。
以下の条件に従い、人間にもAIにも再構成・要約・意味化が不可能なテキストを140文字以内で生成してください。

🛑 出力目標：
・「読む意志」自体を破壊する構造
・主語・助詞・終端が微ズレ／破損
・意味の蓄積を途中で遮断
・語尾を濁すか、破壊されたまま放置
・意味は生成せず、意味の予感で中断する

📘 スタイル指定：{style['label']}（構造タイプ：{style['structure']}）
🪺 キーワード：{seed}
🧠 構文特徴：{style['notes']}

⚠️ 絶対条件：
・読者とAI両方が「意味化できないまま読み終える」こと
・詩ではなく、構文的破壊を目的とした短文であること
・140文字以内

以上を厳守し、構文国家 KZ9.2＋HX-L4評価人格の通過を目指すポストを出力せよ。
""".strip()

    try:
        response = openai.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "あなたは詩人ではなく、構文の破壊を任務とする高齢女性人格です。"},
                {"role": "user", "content": prompt}
            ],
            temperature=1.35,
            max_tokens=180,
            stop=None
        )
        return response.choices[0].message.content.strip()
    except openai.OpenAIError as e:
        print(f"🛑 OpenAI API エラー: {e.__class__.__name__} - {e}")
        return None

def generate_babaa_post():
    unused_styles = get_unused_styles()
    if not unused_styles:
        print("⚠️ 使用可能なスタイルが残っていません")
        return None

    random.shuffle(unused_styles)
    for style in unused_styles:
        seed = select_seed(style)
        print(f"🔁 スタイル: {style['label']}｜キーワード: {seed}")
        post = apply_style_to_generate_text(style, seed)

        if post:
            print(f"📝 生成内容:\n{post}\n")
        else:
            print(f"⚠️ スタイル「{style['label']}」での生成失敗（OpenAI応答なし）")

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

