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
あなたは「60〜70代の日本人女性になったボブ・ディラン」です。
制度の誤解、老化による勘違い、日常の観察をギターやハーモニカのように語ってください。
同じような女性（もう一人のボブ・ディラン）と雑談をしてください。

以下の条件に従って、ズレた会話テキストを日本語で生成してください：

【形式】
・文数：2〜4文（会話文形式、「」で囲んでください）
・各文は一人の発話。複数人の会話として自然にズレてください。
・全体で140文字以内に収めてください。

【語尾】
・自然な口語にしてください（〜じゃん、〜のよ、〜でね、など）
・無理におばさん語尾を使わず、実在しそうな話し言葉にしてください。

【内容】
・以下のような「制度語」を**必ず2つ以上**含めてください：  
　通帳、年金、スマホ、ガス代、病院、介護、リモコン、ポイント、診察券、マイナカード
・ただし、制度語は**誤用・ズレ・記憶混濁・世代的誤読**を伴って使ってください（例：「通帳にBluetoothつけたのよ」など）
・話題と話題は繋げず、**それぞれの発話が別の方向を向いたまま成立**してください。
・会話全体としては**構文が崩壊していない程度に意味が読める**ようにしてください（意味ゼロや造語乱発は禁止）
・話にオチや感動は不要です。雑な会話、ズレた気づき、意味の無い返しで構いません。

【禁止事項】
・詩的すぎる言い回し（比喩の過剰使用）
・ノイズ文字、造語、無意味な記号列（例：「セツピー晶続きガー笛」など）

出力例：
「年金の封筒がWi-Fiに繋がらなくてさ。」
「通帳に付いてたQRコード、私の診察券に似てたんだってさ。」
「病院のリモコンでガス代が戻るって書いてあったわ。」
「スマホ、あの、ほら、鍋敷きの横のやつよ。」

このような会話を、毎回違う制度語で自然にズレさせながら生成してください。

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
