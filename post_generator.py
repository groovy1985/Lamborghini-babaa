import os
import json
import time
from datetime import datetime
from dotenv import load_dotenv
from openai import OpenAI
import re

# Load environment variables
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
model = os.getenv("OPENAI_MODEL", "gpt-4")

DAILY_LIMIT = 15
DAILY_LIMIT_PATH = "logs/daily_limit.json"
os.makedirs(os.path.dirname(DAILY_LIMIT_PATH), exist_ok=True)

def check_daily_limit():
    today = datetime.now().strftime("%Y-%m-%d")
    if os.path.exists(DAILY_LIMIT_PATH):
        with open(DAILY_LIMIT_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        if data.get(today, 0) >= DAILY_LIMIT:
            print(f"[INFO] 本日分の生成上限（{DAILY_LIMIT}件）に達しました")
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
        json.dump(data, f, ensure_ascii=True, indent=2)

def generate_babaa_post():
    if not check_daily_limit():
        return None

    max_attempts = 10
    for _ in range(max_attempts):
        try:
            jp_prompt = """
You are a 70-year-old Japanese woman living in a quiet town.
Inside you are four whispering minds:
- Bob Dylan (melancholic metaphor),
- Tatekawa Danshi (cynical detours),
- Fyodor Dostoevsky (dark reflections),
- and "Ore" (silent observer).

Please write a 3-line conversation between you and two other elderly women during a casual roadside chat.

[Instructions]
- Each line should be in English and enclosed in double quotes.
- Keep it soft, strange, and slightly surreal.
- Topics can be ordinary (weather, tofu, cats), but each line should have a faint twist (philosophical, poetic, or unsettling).
- Keep the grammar valid and avoid nonsense or modern slang.
- Total length under 280 characters.
""".strip()

            response = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": jp_prompt}],
                temperature=1.2,
                timeout=15,
            )
            english_text = response.choices[0].message.content.strip()
            print(f"[EN] {english_text}")

            translate_prompt = f"""
Please translate the following English into natural, soft, elderly Japanese.
It should sound like a quiet conversation between three Japanese grandmothers, with a slightly poetic or surreal tone.

Preserve the metaphors and structure, but make sure it is grammatically correct and smooth in Japanese.
Translate each line and enclose it in Japanese quotation marks「」.

English:
{english_text}
""".strip()

            translation = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": translate_prompt}],
                temperature=1.0,
                timeout=15,
            )
            japanese_text = translation.choices[0].message.content.strip()
            print(f"[JP] {japanese_text}")

            dialogue_lines = re.findall(r'「.*?」', japanese_text, re.DOTALL)
            text_len = len(re.sub(r'\s', '', japanese_text))
            is_dialogue = bool(dialogue_lines)

            if is_dialogue:
                if 1 <= len(dialogue_lines) <= 4 and text_len <= 140:
                    increment_daily_count()
                    return {"text": "\n".join(dialogue_lines), "timestamp": datetime.now().isoformat()}
            else:
                if 1 <= text_len <= 140:
                    increment_daily_count()
                    return {"text": japanese_text, "timestamp": datetime.now().isoformat()}

            print(f"[WARN] フォーマット不適合：dialogue={is_dialogue}, lines={len(dialogue_lines)}, text_len={text_len}")
            time.sleep(1)

        except Exception as e:
            print(f"[ERROR] APIエラー: {e}")
            time.sleep(2)

    print("[FAILED] 全試行失敗：投稿スキップ")
    return None
