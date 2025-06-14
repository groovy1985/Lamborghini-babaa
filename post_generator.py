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

# Removed outdated fixed GOBI_LIST, allowing natural endings

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
            jp_prompt = f"""
以下の条件で、日本語の構文崩壊型テキストを生成してください。

【バリエーション分岐】
・文数はランダムで2〜4文としてください
・文が2〜4行の場合 → 会話文形式（各文を「」で囲んでください）
・文が1文の場合 → 独白形式（「」なしで、地の文として書いてください）

【語尾仕様】
・語尾は自然で、60〜70代女性の口調に近いリアリズムを意識してください（形式にこだわらなくてよい）


【内容】
・制度語を2つ以上含めてください（例：通帳、病院、年金、スマホ、ガス代など）
・ただし、それらを正確に使わず、誤用・ズレ・すり替えを含んでください
・文と文は意味を連鎖させず、バラバラなままにしてください

【禁止事項】
・抽象語（愛、希望、記憶、夢、自由、救いなど）
・登場人物名、時系列、感動要素、一貫した物語

【出力形式】
・文数2〜4：各文を「」で囲んで会話形式にしてください（句点で閉じてください）
・文数1：独白形式で書いてください（「」を使わず、地の文で書いてください）
・全体で140文字以内にしてください
""".strip()

            response = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": jp_prompt}],
                temperature=1.25,
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
