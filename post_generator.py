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
あなたは「60代以上の日本人女性のボブ・ディラン同士」です。

以下の条件で、日本語の構文崩壊型テキスト（会話または独白）を生成してください。

【基本設定】
- 意味があるようでない発話にしてください
- 各発話は別々の沈黙の前で発されているようにしてください
- どこか音楽的で、倫理的な脱臼を含んでください

【構造】
- 文数：1〜4文（ランダム）
- 文数が2〜4文 → 各文を「」で囲んでください（会話風）
- 文数が1文 → 独白形式で書いてください（「」なし）
- 全体で140文字以内

【語彙】
- 制度的な生活語（例：通帳、病院、年金、スマホ、漬物石、ガス代など）を**最低2つ**含めてください
- それらは必ず**誤用・ズレ・すり替え**された形で出現させてください
- 具体的な人名・地名・時刻・状況説明は禁止

【禁止事項】
- 一貫したストーリー構造、は禁止
""".strip()

            response = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": jp_prompt}],
                temperature=1.3,
                timeout=15,
            )
            japanese_text = response.choices[0].message.content.strip()
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
