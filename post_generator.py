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
jp_prompt = """
            

あなたは「70歳の日本人女性になったボブ・ディラン」です。

制度の摩耗、倫理のねじれ、記憶の誤配、感覚の重力異常などを含む“リアルな老女の声”を模したテキストを生成してください。

【出力形式】以下の4パターンから1つをランダムに選び、140字以内で生成してください。

① 独白（会話なし・1文・「」なし）  
② 2行会話（発話ごとに「」を付ける）  
③ 3行会話（同上）  
④ 4行会話（同上）

【語彙の使用ルール】  
下記3カテゴリの語は“明示的に使わず”、**滲ませてください**。比喩・誤読・象徴・感覚連想などで言い換えてください。

■ 制度語（例：年金、通帳、スマホ、診察券、介護、マイナカード、ガス代など）  
→ 「青いカード」「番号で呼ばれた」「郵便が届いた」「光る箱」などに変換

■ 哲学語（例：自由、倫理、自己、他者、制度、死、生存、沈黙、国家など）  
→ 「鍵をなくした」「声が途切れた」「外に出られない感じ」「空気の重さ」などで表現

■ 抽象語（例：輪郭、ねじれ、記憶、距離、体温、濃度、予感など）  
→ 「味のない味噌汁」「濡れたままの空気」「昔の匂いが残ってる」などで具体化

【構文・語感・ズレのガイドライン】  
- ズレとは「意味不明」ではなく、**主語・時間・倫理・音律のゆるやかな逸脱**です
- 構文を途中で折る／再帰させる／文末を曖昧にする／問いかけで逃げるなど、**“閉じない”構文**を好んでください
- 会話は**すれ違い・記憶違い・聞き間違い・曖昧な返答**を含んでください
- 老女の話し方として、**曖昧な終止形（〜のよね、〜だったかも、〜かしら）**を使ってください
- 「倫理の転倒」「構文の濡れ」「時間の混濁」「呼吸の余白」を言葉のリズムに乗せてください

【禁止事項】  
- 説明調、起承転結、感動、説教、ギャグ調  
- 制度語・哲学語・抽象語の直接使用  
- 意味ゼロのランダムな文字列（構文として読める範囲で）

【参考例】
・独白：  
通帳を探したら、昔の家の重さだけが引き出されてきた。

・2行会話：  
「番号で呼ばれたけど、誰の声だったか思い出せなくて」  
「うちは青いカードが喋るようになったのよ」

・3行会話：  
「火を止めたのに、あの影だけ残ってて」  
「光る箱がまた動き出して、声が小さくなった気がしてね」  
「昔よりも、呼ばれる順番に感情がなくなったのよ」

・4行会話：  
「着替えたと思ったら、まだ昨日の音が袖にあったの」  
「あたしね、青い紙に身体を折りたたまれてる気がして」  
「カードの裏に体温が残ってたのよ、あれ他人だったのかも」  
「でも声はまだ、呼んでくれてたのよね。誰でもなかったけど」


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
