import os
import time
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

# ✅ 禁止語句（詩的・感情系）
FORBIDDEN_WORDS = ["太陽", "虹", "涙", "夢", "心", "美しい", "希望", "祈り", "光", "空", "音", "調和"]

# ✅ 日次制限（15件まで）
DAILY_LIMIT_PATH = "logs/daily_limit.json"
DAILY_LIMIT = 15

def check_daily_limit():
    today = datetime.now().strftime("%Y-%m-%d")
    if os.path.exists(DAILY_LIMIT_PATH):
        with open(DAILY_LIMIT_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        if data.get(today, 0) >= DAILY_LIMIT:
            print(f"🚫 本日分の生成上限に達しました")
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

# ✅ 禁止パターン検査
def contains_illegal_patterns(text: str) -> bool:
    if re.search(r"[a-zA-Z]{5,}", text): return True
    if re.search(r"[^\u3040-\u30FF\u4E00-\u9FFF。、！？「」ーぁ-んァ-ン0-9\s]", text): return True
    if len(text) > 140 or len(text) < 15: return True
    if "「" not in text or "」" not in text: return True
    for word in FORBIDDEN_WORDS:
        if word in text:
            print(f"❌ 禁止語句検出: {word}")
            return True
    return False

# ✅ 翻訳
def translate_to_japanese(english_text: str) -> str:
    prompt = (
        "以下の英文は老婆2人の短い会話です（A→B）。\n"
        "詩的・感情的な表現は禁止です。ズレた会話を日本語2行で訳してください。\n"
        "140字以内、独白は禁止、意味がつながらなくて構いません。\n\n"
        f"{english_text}\n\n日本語："
    )
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=1.1
    )
    return response.choices[0].message.content.strip()

# ✅ メイン生成関数
def generate_babaa_post():
    if not check_daily_limit():
        return None

    attempts = 6

    while attempts > 0:
        try:
            system_prompt = (
                "You are BabaaBot. Generate only 2 lines of Japanese dialogue between two old women. "
                "The conversation must be broken, strange, and misaligned. No poetry. No emotion. No monologue."
            )
            user_prompt = (
                "Generate a surreal A→B Japanese conversation (2 lines only). "
                "The logic should be broken or absurd. No beauty. No clarity."
            )
            en_response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=1.2
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
                increment_daily_count()
                return {
                    "text": final,
                    "tags": [],
                    "style_id": "minimal_fast",
                    "timestamp": datetime.now().isoformat()
                }
            else:
                print("❌ 投稿冷却／構文不成立")
                attempts -= 1

        except Exception as e:
            print(f"❌ APIエラー: {e}")
            attempts -= 1
            time.sleep(1)

    print("🚫 全試行失敗：ポスト生成スキップ")
    return None
