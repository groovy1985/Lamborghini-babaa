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
日本のどこにでもいそうな、少し抽象的で、少しとぼけたおばあさんたちの**井戸端会議の一節**を、3行で書いてください。

【出力仕様】
- 出力は**必ず3行の会話形式**
- 各行の発話は「」で囲ってください
- 全体で**140文字以内**

【内容の特徴】
- 会話の内容は**とことん薄くてよい**（例：食べ物、天気、テレビ、猫、昔話のかけらなど）
- ただし、**抽象的・哲学的なニュアンスが軽く滲んでいること**
  - 「昨日が薄い気がしてね」  
  - 「名前じゃなかったのかもしれないのよ」  
  - 「匂いが残ったのか、気配が先だったのか」  
  のように、“ちょっと引っかかる違和感”や“どこかへ行ってしまった意味”が少しだけ残るようにしてください

【語彙の扱い】
- 哲学語・抽象語（自由、記憶、他者、ねじれ、輪郭など）は、**そのままでは使わず、含意・匂いとして滲ませてください**
  - 例：「味があるのに味がしない」「誰かの声だった気がする」「昔のままでも残ってない」

【話し方】
- 老女らしい自然な口調を使ってください（例：「〜のよ」「〜だったかしら」「〜って言ったじゃない」など）
- 文法は自然な日本のおばさん達の会話文にしてください。
- ただし、完全に意味の通らない構文（ノイズ）は避けてください


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
