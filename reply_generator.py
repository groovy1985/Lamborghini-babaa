import os
import json
import time
import re
from datetime import datetime
from dotenv import load_dotenv
from openai import OpenAI

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

def extract_keyword_from_text(text):
    keywords = re.findall(r'[一-龯]{2,}|[ァ-ヶー]{2,}', text)
    if keywords:
        print(f"[INFO] 抽出キーワード: {keywords[0]}")
        return keywords[0]
    return "思い出"

def generate_babaa_post(context_text):
    if not check_daily_limit():
        return None

    keyword = extract_keyword_from_text(context_text)[:10]
    max_attempts = 10

    for _ in range(max_attempts):
        try:
            en_prompt = f"""
You are an 80-year-old Japanese woman living in a crumbling housing complex.

Generate one grammatically correct English sentence as a quiet monologue, inspired by:
"{keyword}"

[Guidelines]
- Begin with a physical or sensory trigger (smell, ache, noise).
- Include the keyword naturally.
- Insert a strange, reality-bending metaphor tied to daily life (e.g. food, medicine, memory).
- Let the sentence feel subtly broken, ethically or logically off.
- Avoid poetry, names, or slang.
- Output only one sentence, nothing else.
""".strip()

            response = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": en_prompt}],
                temperature=1.2,
                timeout=10,
            )
            english_text = response.choices[0].message.content.strip()
            print(f"[EN] {english_text}")

            translate_prompt = f"""
以下の英文を、80歳の女性の自然な独白として翻訳してください。

[条件]
- 1文のみ／20〜100文字（空白除く）
- 文法は正しいが、意味がどこか壊れている
- 「{keyword}」を含めてください
- 冒頭は感覚的なきっかけ（匂い・痛みなど）で始めてください
- 語尾は「〜だわ」「〜のよ」「〜ね」などババァ的に
- 詩的美文は禁止。生活に根差した唐突なイメージはOK
- 出力は文章のみ。記号・説明なし
""".strip()

            translation = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": translate_prompt + "\n\n" + english_text}],
                temperature=1.0,
                timeout=15,
            )
            japanese_text = translation.choices[0].message.content.strip()
            print(f"[JP] {japanese_text}")

            clean_text = re.sub(r'\s', '', japanese_text)
            if 20 <= len(clean_text) <= 100 and "。" not in japanese_text:
                increment_daily_count()
                return {
                    "text": japanese_text,
                    "timestamp": datetime.now().isoformat(),
                    "keyword": keyword
                }

            print(f"[WARN] 不適合（長さ: {len(clean_text)} 文字）→再試行")
            time.sleep(1)

        except Exception as e:
            print(f"[ERROR] APIエラー: {e}")
            time.sleep(2)

    print("[FAILED] 全試行失敗：投稿スキップ")
    return None