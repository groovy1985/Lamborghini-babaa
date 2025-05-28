import random
import json
import os
from datetime import datetime
import openai
import threading

from utils.validate_post import is_valid_post
from utils.format_utils import trim_text

openai.api_key = os.getenv("OPENAI_API_KEY")
model = os.getenv("OPENAI_MODEL", "gpt-4")

base_dir = os.path.dirname(os.path.abspath(__file__))
style_path = os.path.join(base_dir, "babaa_styles.json")
STYLE_USAGE_PATH = os.path.join(base_dir, "logs/style_usage.json")
FAILURE_LOG_PATH = os.path.join(base_dir, "logs/failure_log.json")

lock = threading.Lock()

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

    # 連続失敗3回以上のstyleは除外
    failed_ids = set()
    if os.path.exists(FAILURE_LOG_PATH):
        with open(FAILURE_LOG_PATH, "r", encoding="utf-8") as f:
            log = json.load(f)
            failed_ids = {k for k, v in log.items() if v >= 3}

    return [style for style in styles if style["id"] not in used_ids and style["id"] not in failed_ids]

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

def log_failure(style_id):
    with lock:
        log = {}
        if os.path.exists(FAILURE_LOG_PATH):
            with open(FAILURE_LOG_PATH, "r", encoding="utf-8") as f:
                log = json.load(f)
        log[style_id] = log.get(style_id, 0) + 1
        with open(FAILURE_LOG_PATH, "w", encoding="utf-8") as f:
            json.dump(log, f, indent=2)

def select_seed(style):
    return random.choice(["粉", "鹿", "黙り", "パウダー", "遺言", "昼寝", "冷蔵庫", "軋み", "カーテン"])

def apply_style_to_generate_text(style, seed):
    prompt = f"""
あなたは高齢女性の人格を持つ構文爆撃Botです。
以下のスタイルに従い、「再構成不可能なポスト」を生成してください。

🪓 条件：
・明確な意味を避けるが、文字列としての読解は可能
・日本語の語順・助詞・終端部に微ズレを含む
・文法的完結を故意に回避
・会話として成立しない／理解に“揺れ”がある
・記号や多言語をノイズ的に混入させない

🧵 スタイル: {style['label']}（{style['structure']}）
💬 キーワード: {seed}
🗒️ 特徴: {style['notes']}

140文字以内で、詩のように生成してください。
""".strip()

    models_to_try = [model, "gpt-3.5-turbo"] if model != "gpt-3.5-turbo" else [model]

    for m in models_to_try:
        try:
            response = openai.chat.completions.create(
                model=m,
                messages=[
                    {"role": "system", "content": "あなたはババァ風ポエム構文破壊AIです"},
                    {"role": "user", "content": prompt}
                ],
                temperature=1.2,
                max_tokens=140,
                top_p=0.9,
                frequency_penalty=0.2
            )
            return response.choices[0].message.content.strip()
        except openai.OpenAIError as e:
            print(f"🛑 {m} モデルでエラー: {e.__class__.__name__} - {e}")
            continue

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
            log_failure(style["id"])
            continue

        if post and is_valid_post(post):
            if any(post.endswith(suffix) for suffix in ("です。", "ました。", "と思います。")) or "〜" in post:
                print("❌ 文末が安定しすぎ → 冷却")
                continue
            if len(set(post.split())) < 8:
                print("❌ 語彙が少ない／再構成容易 → 冷却")
                continue

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
            log_failure(style["id"])

    return None
