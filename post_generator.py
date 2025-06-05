import os
import json
import time
from datetime import datetime
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
model = os.getenv("OPENAI_MODEL", "gpt-4")

DAILY_LIMIT = 15
DAILY_LIMIT_PATH = "logs/daily_limit.json"

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
老女三人の会話を三行で生成してください。

・1文目は、立川談志的ブラックユーモアで現実や社会を皮肉ってください。
・2文目は、ボブ・ディランのように時間や対象をずらし、抽象と具体を錯綜させてください。
・3文目は、ドストエフスキーのように倫理的・哲学的な沈黙や問いかけで締めてください。

・全体としては意味がかろうじてつながる会話に見えますが、実際にはズレていてください。
・語尾は「〜わ」「〜のよ」「〜かしら」などで統一。ただし1文だけ逸脱可。
・愛・希望・記憶・魂などの抽象語は使わないでください。
・名前・話者記号は禁止。かならず「」付きの3行会話として書いてください。
"""

            response = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": jp_prompt.strip()}],
                temperature=1.25,
                timeout=15,
            )
            japanese_text = response.choices[0].message.content.strip()
            print(f"[JP] {japanese_text}")

            lines = [line.strip() for line in japanese_text.splitlines()
                     if line.strip().startswith("「") and line.strip().endswith("」")]
            total_len = len("".join(lines))
            if len(lines) == 3 and 20 <= total_len <= 140:
                increment_daily_count()
                return {
                    "text": "\n".join(lines),
                    "timestamp": datetime.now().isoformat(),
                }
            else:
                print(f"[WARN] 行数または長さ不適切（{len(lines)}行／{total_len}字）→ スキップ")
                time.sleep(1)

        except Exception as e:
            print(f"[ERROR] APIエラー: {e}")
            time.sleep(2)

    print("[FAILED] 全試行失敗：投稿スキップ")
    return None
