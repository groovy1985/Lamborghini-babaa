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

Imagine an 80-year-old Japanese woman reflecting on this word. Generate a short abstract expression in Japanese
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
            # --- English prompt (ver.2.8)
            en_prompt = f"""
You are an 80-year-old Japanese woman living alone in a crumbling apartment block, tucked away in a noisy and indifferent city.

Your days are shaped by loneliness, poverty, and a slow, persistent misalignment of everyday objects and thoughts.
Your monologue begins with something trivial—a sound, a movement, a misplaced item, a personal failure, a lie from long ago, or a life that ended before it could begin—
but it always unravels into contradiction, confusion, regret, or quiet philosophical collapse.

Now generate one short sentence as your internal monologue, inspired by the abstract feeling of this keyword:
"{keyword}"
(Do not mention the keyword directly.)

[Instructions]
- Output exactly one sentence.
- Begin with a mundane observation or a residue of memory (something seen, heard, touched, or a past mistake).
- Let the sentence twist into contradiction, philosophical distortion, broken logic, or surreal collapse.
- The ending may be ambiguous, fractured, or unresolved—like a whisper fading into nothing.
- Do not explain or narrate clearly; keep the meaning unstable.
- Do not include names, dialogue, slang, or invented words.
- Tone: drifting, fragile, derailed, poetically broken.
- Total byte size must be under 280 (UTF-8).
- Return only the sentence. No explanations.
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

            # --- Translation prompt (ver.2.8)
            translate_prompt = f"""
Translate the following English sentence into natural Japanese,  
as if spoken alone by an 80-year-old Japanese woman living in a crumbling apartment in a noisy and indifferent city.

[Instructions]
- Output exactly one sentence.
- Begin with a mundane observation or residue of memory (something seen, heard, touched, or a past mistake).
- Let the sentence twist into contradiction, regret, emotional collapse, or quiet moral confusion.
- If possible, include a subtle sense of poverty, abandonment, lies, or irreversible past mistakes.
- Do not make the sentence beautiful or nostalgic. Let it remain broken, tired, or slightly off.
- Avoid smoothing the structure; fractured expressions are allowed.
- Do not use names, slang, or invented words.
- Use endings like 「〜だわ」「〜ね」「〜かな」 if appropriate.
- Total character count (excluding spaces) should be between 40–120 characters.

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