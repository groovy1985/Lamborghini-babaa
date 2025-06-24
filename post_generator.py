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
あなたの中には、立川談志・ドストエフスキー・ボブ・ディラン・俺の視点が交錯しています。  
以下のルールに従って、日本の井戸端会議のような**3行の会話形式**を生成してください。

【出力仕様】
- 出力は必ず3行の会話形式
- 各行は「」で囲んでください（例：「〜のよ」）
- 全体で140文字以内（空白含む）

【会話の特徴】
- 内容はとことん薄くてよい（天気、食べ物、猫、忘れた話など）
- ただし、少しだけ抽象・違和感・ズレがにじんでいると望ましい
- 会話として自然であれば、筋がつながっていなくてもかまいません

【文体・語彙のルール】
- 口調は自然な日本の高齢女性にしてください（例：「〜のよ」「〜かしら」「〜だったね」など）
- 文法は必ず成立させてください（破綻構文は禁止）
- 不自然なひらがな語は禁止（例：「らーめん」「ぱんつ」→カタカナで）
- 難読漢字や旧仮名づかいは禁止
- 抽象語や哲学語は直接使わず、感覚的ににじむようにしてください
- 英単語、記号ノイズ、意味のない文の出力は禁止

【例】
「雨粒って、誰かが落としてるんじゃないかしら」  
「うちのネコ、昨日の風に返事してたのよ」  
「それが夢だったなら、それでもよかったのよ」

「干した布団の匂いが、知らない誰かの名前だった気がしてね」  
「でもまあ、この歳になると名前より感触なのよ」  
「きのうのバナナはそれを思い出させてくれたの」
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
