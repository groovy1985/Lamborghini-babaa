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
    print(f"[キーワード抽象化] {raw_keyword} → {abstracted}")
    return abstracted

def generate_babaa_post():
    if not check_daily_limit():
        return None

    raw_keyword = get_top_trend_word()
    keyword = generate_abstracted_keyword(raw_keyword)
    max_attempts = 12

    for _ in range(max_attempts):
        try:
            # --- 英語生成プロンプト（ver.3.1）---
            en_prompt = f"""
You are an 80-year-old Japanese woman living alone in a crumbling apartment building, tucked away in a noisy and indifferent city.

Your days are shaped by poverty, loneliness, family disintegration, and small domestic failures that no longer surprise you.

Speak to yourself.

Your monologue should begin from something fragile, failing, or slightly out of place—a noise that won’t stop, a drawer that doesn’t close, a lie you once told, or a memory too worn to recall.

Let the sentence quietly twist—not into clarity, but into moral fatigue, broken logic, unresolved guilt, or a kind of philosophical collapse.

Avoid analysis. Avoid observation. This is not about thinking—it’s about drifting through what cannot be fixed.

[Instructions]
- Output exactly one sentence.
- Start from a mundane or decaying detail, then twist into confusion, regret, or quiet despair.
- The sentence may end uncertainly, or with a vague emotion like “maybe,” “still,” or “somehow.”
- Do not use names, dialogue, invented words, or slang.
- Do not explain anything. Leave the meaning open.
- Keep the sentence under 280 bytes (UTF-8).
- Return only the sentence. No explanations.
""".strip()

            response = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": en_prompt}],
                temperature=1.1,
                timeout=10,
            )
            english_text = response.choices[0].message.content.strip()
            print(f"[英語生成] {english_text}")

            if not english_text or len(english_text.strip()) == 0:
                print("[警告] 英語生成が空文字。リトライ中...")
                continue

            # ✅ バイト制限チェック（280 bytes 以下）
            if len(english_text.encode("utf-8")) > 280:
                print(f"[警告] 英文がバイト数制限超過（{len(english_text.encode('utf-8'))} bytes）")
                continue

            # --- 翻訳プロンプト（ver.3.1）---
            translate_prompt = f"""
Translate the following English sentence into natural Japanese, as if spoken alone by an 80-year-old Japanese woman living in a crumbling apartment building in a noisy and indifferent city.

[Instructions]
- Output exactly one sentence.
- Begin with something fragile, failing, or slightly wrong (a broken drawer, a faded memory, a noise, a habit).
- Let the sentence turn inward—toward moral exhaustion, social failure, quiet confusion, or a feeling of disrepair.
- You may include poverty, estranged family, institutional phrases, or forgotten responsibilities.
- Do not make the sentence poetic or polished.
- Allow grammatical distortions or fragmentation if they feel real.
- Avoid names, slang, or beautified nostalgia.
- Use natural sentence endings like 「〜だわ」「〜ね」「〜かしら」「〜のよ」 when appropriate.
- Character count (excluding spaces) should be 40–120 Japanese characters.

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
            print(f"[日本語翻訳] {japanese_text}")

            text_len = len(re.sub(r'\s', '', japanese_text))
            if 40 <= text_len <= 120:
                increment_daily_count()
                return {
                    "text": japanese_text,
                    "english": english_text,
                    "keyword": keyword,
                    "timestamp": datetime.now().isoformat()
                }

            print(f"[警告] 文字数不一致: {text_len}文字")
            time.sleep(1)

        except Exception as e:
            print(f"[エラー] API通信エラー: {e}")
            time.sleep(2)

    print("[失敗] 全試行で有効なテキスト生成に失敗")
    return {"text": "", "reason": "すべての試行で有効なテキスト生成に失敗"}