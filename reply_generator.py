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
    # 2文字以上の漢字 or カタカナ単語を優先的に抽出
    keywords = re.findall(r'[一-龯]{2,}|[ァ-ヶー]{2,}', text)
    if keywords:
        print(f"[INFO] 抽出キーワード: {keywords[0]}")
        return keywords[0]
    return "思い出"  # fallback

def generate_babaa_reply(context_text):
    if not check_daily_limit():
        return None

    keyword = extract_keyword_from_text(context_text)[:10]
    max_attempts = 12

    for _ in range(max_attempts):
        try:
            en_prompt = f"""
You are a 70-year-old Japanese woman living in a small town.

Generate a 3-line conversation between you and two elderly women reacting indirectly to this tweet:
"{context_text}"

[Instructions]
- Each line must be in Japanese-style quotation marks, e.g. "The cat didn’t say a word, but I answered anyway."
- Output exactly 3 lines.
- Total character count (excluding spaces) must be under 280.
- Include the word "{keyword}" in at least one line.
- Let each line carry hints of defeat, resignation, or odd wisdom about mundane struggles like bills or loneliness.
- Avoid personal names, nonsense words, or modern slang.
- Use gentle, grandmotherly, conversational English—not formal prose.
- Grammar must be correct; avoid sentence fragments or hallucinated words.

Return only the 3 lines, no extra explanation.
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
次の英語の3行会話を日本語の自然な高齢女性の会話に翻訳してください。

[ルール]
- 各行は「」で囲んでください。
- 出力は必ず3行。
- 総文字数は50〜145文字以内にしてください。
- 個人名・固有名詞は禁止。
- ババァらしいとぼけた口調にしつつ文法は正しく。
- 哲学的表現は生活感に置き換え、自然な会話にしてください。
- 必ず1行に「{keyword}」を含めてください。

翻訳対象:
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

            if len(dialogue_lines) == 3 and 50 <= text_len <= 145:
                increment_daily_count()
                return {"text": "\n".join(dialogue_lines), "timestamp": datetime.now().isoformat()}

            print(f"[WARN] フォーマット不適合：lines={len(dialogue_lines)}, text_len={text_len}")
            time.sleep(1)

        except Exception as e:
            print(f"[ERROR] APIエラー: {e}")
            time.sleep(2)

    print("[FAILED] 全試行失敗：投稿スキップ")
    return None
