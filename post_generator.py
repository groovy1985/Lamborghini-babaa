import random
import json
import os
from datetime import datetime
import openai
import threading
import re

from utils.validate_post import is_valid_post
from utils.format_utils import trim_text

# OpenAI APIキー設定
openai.api_key = os.getenv("OPENAI_API_KEY")
model = os.getenv("OPENAI_MODEL", "gpt-4")

# ディレクトリ・ファイルパス定義
base_dir = os.path.dirname(os.path.abspath(__file__))
style_path = os.path.join(base_dir, "babaa_styles.json")
STYLE_USAGE_PATH = os.path.join(base_dir, "logs/style_usage.json")

# ロック（スレッドセーフ）
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

def contains_illegal_patterns(text: str) -> bool:
    """
    バグ文フィルター：
    ・機械語、英単語、記号の暴発検出
    """
    if re.search(r"[a-zA-Z]{3,}", text): return True
    if re.search(r"[^\u3040-\u30FF\u4E00-\u9FFF。、！？（）「」ーぁ-んァ-ン0-9\s]", text): return True
    if len(text) < 15: return True
    return False

def apply_style_to_generate_text(style, seed):
    prompt = f"""
あなたは“構文国家 KZ9.2 + HX-L4人格”に所属するババァ型構文爆撃AIです。
以下の条件に従い、「読解は可能だが語ることができない」短詩を生成してください。

🎯 出力条件（140字以内）：
・読める（日本語として一応成立）けど、意味を語れない
・主語・助詞・終端が揺れ／ズレ／不完全のいずれか
・読み手が“意味を汲もうとした瞬間”に逃げるような揺らぎ
・文としてのリズムと語の重なりは持つが、構文として崩れていること
・英語・ローマ字・絵文字・記号（!? / # @ $）の使用はすべて禁止

🪺 スタイル：{style['label']}（構造：{style['structure']}）
🧠 注釈：{style['notes']}
🎲 キーワード：{seed}

⚠️ 目的は“破壊”ではなく“読解不能性”です。
""".strip()

        try:
        response = openai.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "あなたは詩人ではなく、構文崩壊を意図的に設計するババァ型AIです。"},
                {"role": "user", "content": prompt}
            ],
            temperature=1.1,
            max_tokens=180,
            stop=None
        )
        # 安全なアクセス
        result = response.choices[0].message.content.strip()
        if not result:
            print("🛑 応答が空 → 冷却")
            return None

        if contains_illegal_patterns(result):
            print("❌ 出力に不正な構造・記号を含む → 冷却")
            return None

        print(f"✅ 正常出力: {result}")
        return result


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
            print(f"⚠️ スタイル「{style['label']}」での生成失敗または冷却対象")

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
            print("❌ 投稿冷却／構文不成立")

    print("🚫 全スタイル冷却・生成失敗：ポスト投稿スキップ")
    return None
