import random
import json
import os
from datetime import datetime
import openai
import threading
import re
import time
from dotenv import load_dotenv

from utils.validate_post import is_valid_post
from utils.format_utils import trim_text

# 環境変数読み込み
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")
model = os.getenv("OPENAI_MODEL", "gpt-4")

# パス設定
base_dir = os.path.dirname(os.path.abspath(__file__))
style_path = os.path.join(base_dir, "babaa_styles.json")
STYLE_USAGE_PATH = os.path.join(base_dir, "logs/style_usage.json")
DAILY_LIMIT_PATH = os.path.join(base_dir, "logs/daily_limit.json")

# 制限設定
DAILY_LIMIT = 5
MAX_GLOBAL_ATTEMPTS = 12

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

def check_daily_limit(limit=DAILY_LIMIT):
    today = datetime.now().strftime("%Y-%m-%d")
    if os.path.exists(DAILY_LIMIT_PATH):
        with open(DAILY_LIMIT_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        if data.get(today, 0) >= limit:
            print(f"🚫 本日分の生成上限（{limit}件）に達しました")
            return False
    return True

def increment_daily_count():
    today = datetime.now().strftime("%Y-%m-%d")
    data = {}
    if os.path.exists(DAILY_LIMIT_PATH):
        with open(DAILY_LIMIT_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
    data[today] = data.get(today, 0) + 1
    with open(DAILY_LIMIT_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def select_seed(style):
    return random.choice(["粉", "鹿", "黙り", "パウダー", "遺言", "冷蔵庫", "昼寝", "軋み", "カーテン", "団子"])

def contains_illegal_patterns(text: str) -> bool:
    if re.search(r"[a-zA-Z]{5,}", text): return True
    if re.search(r"[^\u3040-\u30FF\u4E00-\u9FFF。、！？（）「」ーぁ-んァ-ン0-9\s]", text): return True
    if len(text) < 15: return True
    if re.fullmatch(r"[。、！？ー（）\s]+", text): return True
    return False

def apply_style_to_generate_text(style, seed, max_retries=3):
    prompt = f"""
あなたは“構文国家 KZ9.2 + HX-L4人格”に所属するババァ型構文爆撃AIです。

💬 出力条件：
・短い独白か会話であること（「あたしね…」「…でもさ」など）
・文法的にはギリ読めるが、意味化・要約はできない
・会話として成立しそうで、語尾・助詞がズレて崩れる
・途中で別の話題へ飛ぶ／言いかけ／曖昧語が含まれる
・記号、英語、絵文字、カタカナ語、機械語は使用しない
・140字以内、タグ無し、詩的であってはならない

🎲 キーワード：{seed}
🪺 スタイル：{style['label']}（構造：{style['structure']}）

以上を満たす一文を生成してください。
""".strip()

    for attempt in range(max_retries):
        try:
            response = openai.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "あなたは詩人ではなく、高齢女性の揺れる会話文を生成するAIです。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=1.0,
                max_tokens=120
            )
            result = response.choices[0].message.content.strip()
            if not result:
                print("🛑 応答が空 → 冷却")
                return None
            if contains_illegal_patterns(result):
                print("❌ 不正記号・英語・短文 → 冷却")
                return None
            return result
        except openai.RateLimitError:
            wait_time = 2 ** attempt
            print(f"⏳ API制限：待機 {wait_time}秒（{attempt + 1}回目）")
            time.sleep(wait_time)
        except openai.OpenAIError as e:
            print(f"🛑 OpenAI API エラー: {e.__class__.__name__} - {e}")
            return None
    print("🚫 再試行上限：冷却対象")
    return None

def generate_babaa_post():
    if not check_daily_limit():
        return None

    unused_styles = get_unused_styles()
    if not unused_styles:
        print("⚠️ 使用可能なスタイルが残っていません")
        return None

    random.shuffle(unused_styles)
    remaining_attempts = MAX_GLOBAL_ATTEMPTS

    for style in unused_styles:
        if remaining_attempts <= 0:
            break

        seed = select_seed(style)
        print(f"🔁 スタイル: {style['label']}｜キーワード: {seed}")
        post = apply_style_to_generate_text(style, seed)
        time.sleep(1)

        if post:
            print(f"📝 生成内容:\n{post}\n")
        else:
            print(f"⚠️ スタイル「{style['label']}」での生成失敗または冷却対象")

        if post and is_valid_post(post):
            post = trim_text(post)
            mark_style_used(style["id"])
            increment_daily_count()
            return {
                "text": post,
                "tags": [],
                "style_id": style["id"],
                "timestamp": datetime.now().isoformat()
            }
        else:
            print("❌ 投稿冷却／構文不成立")
            remaining_attempts -= 1

    print("🚫 全スタイル冷却・生成失敗：ポスト投稿スキップ")
    return None
