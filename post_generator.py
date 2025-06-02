import os
import json
import time
from datetime import datetime
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
model = os.getenv("OPENAI_MODEL", "gpt-4")

DAILY_LIMIT = 15
DAILY_LIMIT_PATH = "logs/daily_limit.json"


def check_daily_limit():
    today = datetime.now().strftime("%Y-%m-%d")
    if os.path.exists(DAILY_LIMIT_PATH):
        with open(DAILY_LIMIT_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        if data.get(today, 0) >= DAILY_LIMIT:
            print(f"\U0001f6d1 本日分の生成上限（{DAILY_LIMIT}件）に達しました")
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


def generate_babaa_post():
    if not check_daily_limit():
        return None

    max_attempts = 10
    for _ in range(max_attempts):
        try:
            en_prompt = (
                "Write a short dialogue between two old women, A and B. "
                "The conversation must be completely misaligned and end with an eccentric comment by A. "
                "Use surreal or logically unstable language. No poetry, no beauty. Just 3 lines: A→B→A."
            )

            en_response = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": en_prompt}],
                temperature=1.4
            )
            english_text = en_response.choices[0].message.content.strip()
            print(f"\U0001f310 EN: {english_text}")

            ja_prompt = (
                f"Translate the following dialogue into natural Japanese as if two eccentric elderly women are speaking.\n"
                f"Keep it plain and short. No embellishment.\n\n{english_text}\n\nJapanese:")

            ja_response = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": ja_prompt}],
                temperature=1.0
            )
            japanese_text = ja_response.choices[0].message.content.strip()
            print(f"\U0001f238 JP: {japanese_text}")

            total_len = len(japanese_text.replace("\n", "").strip())
            if 20 <= total_len <= 140:
                increment_daily_count()
                return {
                    "text": japanese_text,
                    "timestamp": datetime.now().isoformat(),
                    "english": english_text
                }
            else:
                print(f"⚠️ 長さ不適切（{total_len}字）→ スキップ")
                time.sleep(1)

        except Exception as e:
            print(f"❌ APIエラー: {e}")
            time.sleep(2)

    print("🚫 全試行失敗：投稿スキップ")
    return None
