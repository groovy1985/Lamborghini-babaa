import os
import time
import random
import json
import re
from datetime import datetime
from dotenv import load_dotenv
from openai import OpenAI
from utils.validate_post import is_valid_post
from utils.format_utils import trim_text

# ✅ 環境変数読み込み
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
model = os.getenv("OPENAI_MODEL", "gpt-4")

# ✅ ファイルパス定義
base_dir = os.path.dirname(os.path.abspath(__file__))
style_path = os.path.join(base_dir, "babaa_styles.json")
STYLE_USAGE_PATH = os.path.join(base_dir, "logs/style_usage.json")
DAILY_LIMIT_PATH = os.path.join(base_dir, "logs/daily_limit.json")

DAILY_LIMIT = 15
MAX_GLOBAL_ATTEMPTS = 12

# ✅ スタイル読み込み
with open(style_path, "r", encoding="utf-8") as f:
    styles = json.load(f)

# ✅ 補助関数（全て内包）

def check_daily_limit():
    today = datetime.now().strftime("%Y-%m-%d")
    if os.path.exists(DAILY_LIMIT_PATH):
        with open(DAILY_LIMIT_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        if data.get(today, 0) >= DAILY_LIMIT:
            print(f"🚫 本日分の生成上限（{DAILY_LIMIT}件）に達しました")
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

def get_unused_styles():
    used_ids = set()
    if os.path.exists(STYLE_USAGE_PATH):
        try:
            with open(STYLE_USAGE_PATH, "r", encoding="utf-8") as f:
                used = json.load(f)
                if isinstance(used, list):
                    used_ids = set(used)
        except Exception as e:
            print(f"⚠️ style_usage.json 読み込みエラー: {e}")
    return [style for style in styles if style["id"] not in used_ids]

def mark_style_used(style_id):
    used = []
    if os.path.exists(STYLE_USAGE_PATH):
        with open(STYLE_USAGE_PATH, "r", encoding="utf-8") as f:
            try:
                used = json.load(f)
            except Exception as e:
                print(f"⚠️ style_usage.json 読み込みエラー: {e}")
    used.append(style_id)
    with open(STYLE_USAGE_PATH, "w", encoding="utf-8") as f:
        json.dump(used, f, ensure_ascii=False, indent=2)

def select_seed(style):
    return random.choice(["tile", "coin", "closet", "bag", "apron", "soap", "thread"])

def contains_illegal_patterns(text: str) -> bool:
    if re.search(r"[a-zA-Z]{5,}", text): return True
    if re.search(r"[^\u3040-\u30FF\u4E00-\u9FFF。、！？「」ーぁ-んァ-ン0-9\s]", text): return True
    if len(text) > 140: return True
    if "「" not in text or "」" not in text: return True
    if text.count("「") < 2: return True  # 少なくとも2発言分
    return False

# ✅ 翻訳処理（1往復ババァ会話）
def translate_to_japanese(english_text: str) -> str:
    prompt = (
        "以下の英文は老婆2人の短い会話です（A→B）。意味はかみ合っていません。"
        "奇妙な論理で着地し、詩的ではなく、曖昧なまま終わります。"
        "説明・情緒は禁止、Poemkun風の独白は禁止、140文字以内、日本語の会話2行で訳してください：\n\n"
        f"{english_text}\n\n日本語："
    )
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=1.3
    )
    return response.choices[0].message.content.strip()

# ✅ メイン生成関数
def generate_babaa_post():
    if not check_daily_limit():
        return None

    unused_styles = get_unused_styles()
    if not unused_styles:
        print("⚠️ 使用可能なスタイルが残っていません")
        return None

    random.shuffle(unused_styles)
    attempts = MAX_GLOBAL_ATTEMPTS

    for style in unused_styles:
        if attempts <= 0:
            break

        seed = select_seed(style)
        print(f"🔁 スタイル: {style['label']}｜キーワード: {seed}")

        try:
            system_prompt = (
                "You are BabaaBot, generating Japanese dialogue between two old women. "
                "The conversation is broken and misaligned, ending with a surreal or absurd connection. "
                "Only generate 2 lines of dialogue. No narration, no emotion, no poetry."
            )
            user_prompt = (
                f"Generate a short conversation between two elderly women (A→B), with a strange, broken logic. "
                f"End with something eccentric or impossible. Keyword (optional): {seed}"
            )
            en_response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=1.4
            )
            english_text = en_response.choices[0].message.content.strip()
            print(f"🌐 EN: {english_text}")

            translated = translate_to_japanese(english_text)
            print(f"🈶 JP: {translated}")

            if contains_illegal_patterns(translated):
                print("❌ 不正パターン → 冷却")
                attempts -= 1
                continue

            if is_valid_post(translated):
                final = trim_text(translated)
                mark_style_used(style["id"])
                increment_daily_count()
                return {
                    "text": final,
                    "tags": [],
                    "style_id": style["id"],
                    "timestamp": datetime.now().isoformat()
                }
            else:
                print("❌ 投稿冷却／構文不成立")
                attempts -= 1

        except Exception as e:
            print(f"❌ APIエラー: {e}")
            attempts -= 1
            time.sleep(2)

    print("🚫 全スタイル冷却・生成失敗：ポスト投稿スキップ")
    return None
