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
model = os.getenv("OPENAI_MODEL", "gpt-4")  # モデルを環境変数で指定可能

# ディレクトリ・ファイルパス定義
base_dir = os.path.dirname(os.path.abspath(__file__))
style_path = os.path.join(base_dir, "babaa_styles.json")
STYLE_USAGE_PATH = os.path.join(base_dir, "logs/style_usage.json")

# ロック（書き込み競合防止用）
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
                else:
                    print("⚠️ style_usage.json の内容が list ではありません。初期化してください。")
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
                    elif isinstance(loaded, dict):
                        used = list(loaded.values())
                except Exception as e:
                    print(f"⚠️ style_usage.json 読み込みエラー: {e}")
        used.append(style_id)
        with open(STYLE_USAGE_PATH, "w", encoding="utf-8") as f:
            json.dump(used, f, ensure_ascii=False, indent=2)

def select_seed(style):
    return random.choice(["粉", "鹿", "黙り", "パウダー", "遺言", "昼寝", "軋み", "カーテン"])

def apply_style_to_generate_text(style, seed):
    prompt = f"""
あなたは高齢女性の人格を持つ構文破壊AIです。
以下のスタイルに従い、語りかけ未遂・再構成不能な吊り構文を生成してください。

スタイル: {style['label']}（{style['structure']}）
特徴: {style['notes']}

条件:
- 140文字以内
- 再構成・要約・感想を拒否（感想を誘発しない）
- 会話文や意味成立を避ける（途中で止まる言い回し）
- 拍のズレ／音の沈み／語尾の気配のみを残す
- キーワード: {seed}
""".strip()

    try:
        response = openai.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "あなたは意味生成を拒否する構文爆撃ババァです。"},
                {"role": "user", "content": prompt}
            ],
            temperature=1.3,
            max_tokens=160
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
