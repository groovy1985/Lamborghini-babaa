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
    max_attempts = 10

    for _ in range(max_attempts):
        try:
            # --- 英語生成プロンプト（ver.3.3-condensed）---
            en_prompt = f"""
You are an 80-year-old Japanese woman living in a crumbling housing complex.

Write one grammatically correct sentence, inspired by:
"{keyword}"

[Instructions]
- Start with a sensory cue (smell, pain, texture).
- Include a strange metaphor from daily life (medicine, food, loss).
- Let the meaning feel fractured, burdened, or ethically off.
- Let grief or exhaustion leak through. Don’t explain.
- No names, slang, or poetry.
- Output one sentence only.
""".strip()

            response = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": en_prompt}],
                temperature=1.2,
                timeout=10,
            )
            english_text = response.choices[0].message.content.strip()
            print(f"[EN] {english_text}")

            if not english_text or len(english_text.strip()) == 0:
                print("[警告] 英語生成が空文字。リトライ中...")
                continue

            if len(english_text.encode("utf-8")) > 280:
                print(f"[警告] 英文バイト数オーバー: {len(english_text.encode('utf-8'))} bytes")
                continue

            # --- 翻訳プロンプト（ver.3.3-condensed）---
            translate_prompt = f"""
以下の英文を、80歳の女性の自然な独白として翻訳してください。

・出力は1文のみ、20〜100文字。
・必ず「{keyword}」を含めてください。
・冒頭は感覚的な発端で。
・語尾はババァ的に（〜のよ、〜だわ 等）。
・意味が壊れたままでも構いません。
・構文に、説明できない嘆きや疲れを滲ませてください。
・詩的にせず、生活の裂け目から漏れた言葉にしてください。
・記号・装飾は不要です。

英文:
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

            text_len = len(re.sub(r'\s', '', japanese_text))
            if 20 <= text_len <= 100:
                increment_daily_count()
                return {
                    "text": japanese_text,
                    "english": english_text,
                    "keyword": keyword,
                    "timestamp": datetime.now().isoformat()
                }

            print(f"[警告] 長さ不適合（{text_len}文字）")
            time.sleep(1)

        except Exception as e:
            print(f"[ERROR] API通信エラー: {e}")
            time.sleep(2)

    print("[FAILED] 全試行失敗：投稿スキップ")
    return {"text": "", "reason": "すべての試行で有効なテキスト生成に失敗"}