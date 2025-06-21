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

日常と制度の境目で、記憶や体温が曖昧になっていくような、ズレた会話や独白をつくってください。

【出力形式】  
次のどれかをランダムに選び、全体で140字以内にしてください：  
① 独白（会話なし・1行）  
② 2行会話（「」つき）  
③ 3行会話  
④ 4行会話  

【語の扱い】  
以下のような語は**直接使わず**、滲ませてください：

- 制度語（例：年金、通帳、スマホ、診察券、マイナカード）  
　→ 「封筒」「番号」「青い紙」「音が出るやつ」など

- 哲学語（例：自由、他者、制度、倫理、自己、沈黙）  
　→ 「どこにも届かない声」「誰かの代わりにいた気がする」「扉が片方だけ閉まってた」など

- 抽象語（例：距離、ねじれ、濃度、記憶、輪郭、体温）  
　→ 「間がつかめない」「味のない味」「触った感じが残ってた」など

【構文・話し方】  
- 会話には“少しズレた返事”や“誰にも届かないぼやき”を混ぜてください  
- 構文は読める範囲でかまいません。**意味はつながらなくても、声として聞こえるようにしてください**  
- 文末は「〜のよ」「〜だったかしら」「〜じゃなかったっけ」など、**女の含み・逃げ・粘り**を持たせてください

【禁止事項】  
- ストーリー・説明調・感動・説教・意味ゼロの文字列  
- 「自由」「記憶」などの単語をそのまま使うこと


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
