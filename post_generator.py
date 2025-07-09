import os
import json
import time
import re
from datetime import datetime
from dotenv import load_dotenv
from openai import OpenAI
from read_trend import get_top_trend_word

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

def generate_abstracted_keyword(raw_keyword: str) -> str:
    prompt = f"""
The word is: "{raw_keyword}"

Imagine a 70-year-old Japanese woman reflecting on this word. Generate a short abstract expression in Japanese
that captures its feeling or image. Do not invent new words; use only existing Japanese words.
Return only the phrase, no explanation.
""".strip()

    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=1.0,
        timeout=5,
    )
    abstracted = response.choices[0].message.content.strip()
    print(f"[KEYWORD] {raw_keyword} → {abstracted}")
    return abstracted

def generate_babaa_post():
    if not check_daily_limit():
        return None

    raw_keyword = get_top_trend_word()[:10]
    keyword = generate_abstracted_keyword(raw_keyword)
    max_attempts = 12

    for _ in range(max_attempts):
        try:
            en_prompt = f"""
You are a 70-year-old Japanese woman living alone in a decaying apartment block somewhere deep in a modern city.

Each day is shaped by poverty, isolation, and small, almost imperceptible distortions in the world around you.
Your monologue begins with something trivial or mundane—a sound, a gesture, a misplaced object—but always slips toward a quietly broken logic, a philosophical twist, or a surreal sense of collapse.

You are not loud, not angry—you speak in murmurs, in drifting thoughts, as if your voice could vanish mid-sentence.

Now, generate one short English sentence as your internal monologue.
It must be inspired by the abstract feeling of this keyword: "{keyword}"
Do not mention the keyword directly.

[Instructions]
- Write exactly one sentence.
- Start with a mundane sensory observation (something seen, heard, felt).
- Let the sentence bend into philosophical confusion, poetic absurdity, or quiet madness.
- Do not explain or narrate clearly—let it remain ambiguous or incomplete.
- Use no names, no dialogue, no slang, no invented words.
- It should sound fragile, indirect, and strange.
- Total byte size under 280 (UTF-8).

Only return the sentence. No explanations.
""".strip()

            response = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": en_prompt}],
                temperature=1.1,
                timeout=10,
            )
            english_text = response.choices[0].message.content.strip()
            print(f"[EN] {english_text}")

            if not english_text or len(english_text.strip()) == 0:
                print("⚠️ 英語生成が空文字。リトライ中...")
                continue

            translate_prompt = f"""
Translate the following English sentence into natural Japanese, as if spoken by a 70-year-old Japanese woman
living alone in a decaying apartment in Tokyo.

[Instructions]
- Output exactly one sentence.
- It must feel like a quiet, drifting monologue with a sense of philosophical confusion, poverty, or emotional collapse.
- Use abstract imagery or broken logic if needed.
- Avoid clear explanations; let the meaning remain vague or impressionistic.
- Avoid invented words, place names, or slang.
- Gentle endings like 「〜だわ」「〜ね」「〜かな」 can be used if appropriate.
- Length should be 40–120 Japanese characters (excluding spaces).

Here is the English sentence:
{english_text}
""".strip()

            translation = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": translate_prompt}],
                temperature=0.9,
                timeout=15,
            )
            japanese_text = translation.choices[0].message.content.strip()
            print(f"[JP] {japanese_text}")

            text_len = len(re.sub(r'\s', '', japanese_text))
            if 40 <= text_len <= 120:
                increment_daily_count()
                return {
                    "text": japanese_text,
                    "english": english_text,
                    "keyword": keyword,
                    "timestamp": datetime.now().isoformat()
                }

            print(f"[WARN] Length mismatch: text_len={text_len}")
            time.sleep(1)

        except Exception as e:
            print(f"[ERROR] API error: {e}")
            time.sleep(2)

    print("[FAILED] All attempts failed: skipping post")
    return {"text": "", "reason": "すべての試行で有効なテキスト生成に失敗"}