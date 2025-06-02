import os
import json
import time
import re
from datetime import datetime
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv()
client = OpenAI()
model = os.getenv("OPENAI_MODEL", "gpt-4")

DAILY_LIMIT = 15
DAILY_LIMIT_PATH = "logs/daily_limit.json"


def check_daily_limit():
    today = datetime.now().strftime("%Y-%m-%d")
    if os.path.exists(DAILY_LIMIT_PATH):
        with open(DAILY_LIMIT_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        if data.get(today, 0) >= DAILY_LIMIT:
            print(f"⛑️ 本日分の生成上限（{DAILY_LIMIT}件）に達しました")
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
                "Write a 3-turn dialogue between two elderly women.\n"
                "Each line should sound like a reply to the previous line, but must not logically follow it.\n"
                "The tone should be subtly surreal, metaphorical, or uncanny — but not meaningless.\n"
                "Each speaker must seem to respond, yet the meanings should drift apart.\n"
                "Do not use names or speaker labels.\n"
                "Format the dialogue as three lines, each starting with Japanese-style quotes: 「」\n"
                "Example:\n"
                "「I asked the clock if it still remembers Thursdays」\n"
                "「Only the ones that smelled like burnt toast」\n"
                "「My umbrella never forgave me for that」"
            )

            en_response = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": en_prompt}],
                temperature=1.35,
            )
            english_text = en_response.choices[0].message.content.strip()
            english_text = "\n".join(re.findall(r"「.*?」", english_text)) or english_text
            print(f"🌐 EN: {english_text}")

            ja_prompt = (
                f"Translate the following 3-line dialogue into natural Japanese, as if spoken between two elderly women.\n"
                f"Each line should feel like a response, but meanings must remain subtly misaligned.\n"
                f"The tone must be poetic, slightly surreal, and emotionally suggestive.\n"
                f"Keep the form as dialogue, not a monologue.\n"
                f"Use Japanese quote marks (「」) at the start of each line.\n\n{english_text}\n\nJapanese:"
            )

            ja_response = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": ja_prompt}],
                temperature=1.05,
            )
            japanese_text = ja_response.choices[0].message.content.strip()
            print(f"🄸 JP: {japanese_text}")

            lines = [line for line in japanese_text.splitlines() if line.strip()]
            total_len = len("".join(lines))
            if len(lines) == 3 and 20 <= total_len <= 140:
                increment_daily_count()
                with open("logs/generated.jsonl", "a", encoding="utf-8") as f:
                    json.dump({
                        "text": japanese_text,
                        "timestamp": datetime.now().isoformat(),
                        "english": english_text
                    }, f, ensure_ascii=False)
                    f.write("\n")
                return {
                    "text": japanese_text,
                    "timestamp": datetime.now().isoformat(),
                    "english": english_text,
                }
            else:
                print(f"⚠️ 行数または長さ不適切（{len(lines)}行／{total_len}字）→ スキップ")
                time.sleep(1)

        except Exception as e:
            print(f"❌ APIエラー: {e}")
            time.sleep(2)

    print("🚫 全試行失敗：投稿スキップ")
    return None
