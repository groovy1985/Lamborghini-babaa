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

以下の条件に従い、ハーモニカを吹き、ギターを弾き、フォークソングを歌うように
日本の井戸端会話のような3行の会話を生成してください。

【出力仕様】
- 出力は**必ず3行の会話形式**
- 各行は必ず「」で囲むこと（例：「〜のよ」）
- 全体で**140文字以内**に収めること（空白含む）

【会話の特徴】
- 内容はとことん薄くてよい（例：天気、食べ物、猫、昔話など）
- ただし、**ごくうすく抽象・哲学が滲むこと**
  - 例：「昨日が薄い気がしてね」「名前じゃなかったのかもしれないのよ」
- 比喩・象徴・感覚のズレが自然ににじむようにすること

【語尾・語彙・文体のルール】
- 語尾は自然な日本のおばさん口調（例：「〜のよ」「〜だったかしら」「〜してたの」）
- **以下のような語尾は使ってはならない**：
  - 「〜ではや」「〜ますことよ」「〜だったがよ」「〜だというのよ」
- **意味の通らない動詞や造語**（例：「あつかまえて」「つつかみぬいたわ」）は使わないこと
- 抽象語・哲学語（例：自由、真実、記憶、構文）は**直接言わず、匂わせる程度に**
- 句読点や語尾が**不自然にならないよう注意すること**
- ノイズ・乱数・英単語・難読漢字は使用しないこと

【例】
「昨日の雨、ちょっと優しかった気がするのよ」
「濡れた地面に、昔の匂いが混じってたような」
「でもうちの犬は、ぬれてもぜんぜん気にしてなかったわ」
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
