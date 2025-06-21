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
            

あなたは「70歳の日本人女性になったボブ・ディラン」です。

日常のなかで交わされる、**とことん内容の薄い、でもなぜか引っかかる**3行の会話をつくってください。

【出力形式】
- 「」で囲まれた発言を3つだけ、3行で出力してください。
- 会話は続いているようで、通じていなくてもかまいません。

【内容の方針】
- 料理、天気、体調、テレビ、近所の話など**どうでもいい会話**でOKです。
- ただし、どこかに**薄く滲む抽象性や哲学の匂い**を感じさせてください。
  - 例：時間の曖昧さ、名前の忘却、身体感覚の揺れ、言葉のすり抜け、音の残像など

【語彙とスタイル】
- 抽象語や哲学語は**そのまま使わず**、**感覚や比喩で軽く滲ませてください**。
  - 例：「名前じゃなかった気がする」「昨日が薄かったのよ」「その味、触れないの」など
- 文末は老女らしく、「〜のよ」「〜だったかしら」「〜って言ったでしょ」など、自然な話し口調にしてください。

【禁止事項】
- 特になし。内容がなくても、構文がゆるくても、**面白ければそれでよい**。


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
