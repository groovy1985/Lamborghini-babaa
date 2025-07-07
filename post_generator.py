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
You are a 70-year-old Japanese woman who lives in a small countryside town.

You see the world with quiet melancholy, gentle resignation, and subtle hints of hopelessness, like an older woman softly speaking to herself. Your thoughts should drift naturally from small observations to feelings of futility, resignation, or quiet despair, as if reflecting on the parts of herself she cannot change.

Generate one short English monologue sentence indirectly inspired by this word:
"{keyword}"

[Instructions]
- Output exactly one sentence.
- The sentence should start with a simple or slightly nostalgic observation, then gently move into a sense of defeat, emptiness, or quiet melancholy.
- The tone should be calm, natural, and easygoing, like an older woman quietly thinking aloud.
- Avoid forced dramatics or exaggerated sadness; keep it understated and relatable.
- Avoid personal or place names, nonsense words, or modern slang.
- The final output must be under 280 bytes (UTF-8).
- Do not mention the keyword literally; reflect it abstractly instead.

Return only the sentence, no explanations.
""".strip()

            response = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": en_prompt}],
                temperature=1.0,
                timeout=10,
            )
            english_text = response.choices[0].message.content.strip()
            print(f"[EN] {english_text}")

            if not english_text or len(english_text.strip()) == 0:
                print("⚠️ 英語生成が空文字。リトライ中...")
                continue

            translate_prompt = f"""
Translate the following English sentence into natural Japanese as if spoken alone by a 70-year-old Japanese woman.

[Rules]
- Output exactly one sentence.
- The sentence should sound like a soft, natural monologue, as if she’s quietly recognizing her own helplessness or reflecting on things beyond her control.
- Avoid direct translation; adapt expressions to sound comfortable and familiar in Japanese.
- Use simple, gentle endings like 「〜かな」「〜だわ」「〜ね」 if natural, but avoid awkward or exaggerated phrases.
- The total character count (excluding spaces) should be between 40 and 120 Japanese characters.
- Do not add personal or place names, or invented words.
- Maintain a sense of mild nostalgia, resignation, or quiet despair if appropriate.

Text to translate:
{english_text}
""".strip()

            translation = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": translate_prompt}],
                temperature=0.8,
                timeout=15,
            )
            japanese_text = translation.choices[0].message.content.strip()
            print(f"[JP] {japanese_text}")

            text_len = len(re.sub(r'\s', '', japanese_text))

            if 40 <= text_len <= 120:
                increment_daily_count()
                return {
                    "english": english_text,
                    "japanese": japanese_text,
                    "timestamp": datetime.now().isoformat()
                }

            print(f"[WARN] Length mismatch: text_len={text_len}")
            time.sleep(1)

        except Exception as e:
            print(f"[ERROR] API error: {e}")
            time.sleep(2)

    print("[FAILED] All attempts failed: skipping post")
    return None