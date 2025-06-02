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
                "Write a 3-turn dialogue between two elderly women. "
                "The conversation may include surreal or eccentric elements, or resemble proverbs. "
                "What matters is that each line does not logically follow the last. "
                "No names or speaker labels. Format as three lines using Japanese-style quotes: 「」."
            )

            en_response = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": en_prompt}],
                temperature=1.3
            )
            english_text = en_response.choices[0].message.content.strip()
            print(f"\U0001f310 EN: {english_text}")

            ja_prompt = (
                f"Translate the following dialogue into natural Japanese as if two elderly women are speaking.\n"
                f"Use Japanese quote marks（「」）for each line. You may keep eccentric, surreal, or proverb-like tone.\n"
                f"\n{english_text}\n\nJapanese:")

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
