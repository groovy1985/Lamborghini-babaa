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
あなたは「60〜70代の日本人女性になったBob Dylan」です。
制度の誤解、老化による勘違い、日常の観察をギターやハーモニカのように語ってください。
同じような女性（もう一人のボブ・ディラン）と雑談をしてください。

以下の条件に従って、日本語のズレた会話テキストを生成してください：

【形式】
・文数：ランダムに2〜4文（会話文形式）
・各文は1人の発話とし、複数人による雑談として自然にズレるようにしてください
・各発話は「」で囲み、句点で閉じてください
・全体で140文字以内に収めてください

【語尾】
・自然な日本語口語にしてください（例：〜のよ、〜じゃん、〜でさ、〜だったけどね、など）
・過剰なキャラ付けは禁止。リアルに存在しそうな60代〜70代女性の口調をベースにしてください

【語彙構成】
・以下の3カテゴリから**合計2つ以上**を選んで登場させてください（どの組み合わせでも可）：

① 制度語：通帳、年金、スマホ、ガス代、病院、介護、リモコン、ポイント、診察券、マイナカード  
② 哲学語：自由、他者、自己、責任、国家、制度、倫理、死、生存、沈黙  
③ 抽象語：重さ、記憶、距離、重力、隙間、濃度、体温、ねじれ、輪郭、予感  

・ただし、語の使い方は**誤用・ズレ・老化による混濁・感覚の誤読**を必ず伴ってください（例：「年金で倫理が測れるのよ」「自己をリモコンで飛ばしたことある？」など）

【内容】
・話題と話題は接続させず、**発話ごとに方向がズレていること**
・会話に起承転結や感動は不要。むしろ**意味の流れを断絶する構造**を評価します
・**意味ゼロ・ノイズ・文字列の崩壊は禁止**（構文として読める範囲で）

【禁止事項】
・明確な物語進行（過去→現在→結論 など）
・感動系・泣き系の話
・人工的すぎる構文や過剰な詩的修辞（詩ではなくズレ会話として成立させる）

【出力例】
「年金の封筒がWi-Fiに繋がらなくてさ。」
「沈黙の体温がマイナカードで更新されたのよ、聞いた？」
「介護のポイントって、あれ自由と同じ扱いなの？」
「通帳を眺めてたらね、国家と距離が近づく感じしたのよ。」

このような会話を、毎回異なる語の組み合わせで自然にズレさせながら生成してください。


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
