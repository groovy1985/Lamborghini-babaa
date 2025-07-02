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
You are a 70-year-old Japanese woman who lives in a small town.

Inside you, three minds swirl:
- Tatekawa Danshi: cynical, disruptive, derailing.
- Fyodor Dostoevsky: heavy, ethical, obsessed with guilt, salvation, despair.
- Bob Dylan: surreal, fragmented metaphors, dreamlike inversions, musical phrasing.

Generate a 3-line conversation between you and two elderly women reacting indirectly to this tweet:
"{raw_keyword}"

[Instructions]
- Each line must use Japanese-style quotation marks, e.g. "The sun didn’t rise, but I waited anyway."
- Output exactly 3 lines.
- The total combined character count (excluding spaces) must be 140 characters or fewer, and at least 50.
- Each line should contain dense, metaphorical or surreal imagery reminiscent of Dylan.
- Lines must have subtle disjointedness, like the women are talking past each other yet oddly resonating.
- Let each line carry hints of defeat, resignation, melancholy, or absurd wisdom.
- If you can naturally include "{keyword}", do so, but it is optional.
- Avoid personal names, nonsense words, or modern slang.
- Use gentle, grandmotherly, conversational English—not formal or poetic prose.
- Grammar must be correct; no sentence fragments or hallucinations.

Return only the 3 lines, no extra explanation.
""".strip()

            response = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": en_prompt}],
                temperature=1.3,
                timeout=10,
            )
            english_text = response.choices[0].message.content.strip()
            print(f"[EN] {english_text}")

            translate_prompt = f"""
Translate the following 3-line English conversation into natural-sounding Japanese as if spoken by elderly Japanese women.

[Rules]
- Each line must be wrapped in Japanese 「」 quotation marks.
- Use 『』 for emphasis inside 「」 if needed.
- Output must be exactly 3 lines.
- Total combined length should be between 50 and 140 Japanese characters.
- No personal or place names.
- Maintain a "baba-esque" tone: gentle, old-lady-like, with slightly detached or meandering feel.
- Include subtle disjointedness so lines don’t fully connect logically.
- Avoid nonsense, broken grammar, or invented words.
- Replace philosophical or abstract terms with everyday sensory or emotional expressions.
- If you can naturally include 「{keyword}」, do so, but it is optional.

Text to translate:
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

            if len(dialogue_lines) == 3 and 50 <= text_len <= 140:
                increment_daily_count()
                return {"text": "\n".join(dialogue_lines), "timestamp": datetime.now().isoformat()}

            print(f"[WARN] Format mismatch: lines={len(dialogue_lines)}, text_len={text_len}")
            time.sleep(1)

        except Exception as e:
            print(f"[ERROR] API error: {e}")
            time.sleep(2)

    print("[FAILED] All attempts failed: skipping post")
    return None
