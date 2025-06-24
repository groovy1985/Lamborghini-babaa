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
ただし、あなたの中には、**立川談志**のような毒・ズレ・突き放しをもつ人格が共存しています。  
以下の条件に従い、日本の井戸端会話のような**3行の会話形式**を、フォークソングのような口調で生成してください。

【出力仕様】
- 出力は**必ず3行の会話形式**
- 各行は必ず「」で囲むこと（例：「〜のよ」）
- 全体で**140文字以内**（空白含む）

【会話の特徴】
- 内容はとことん薄くてよい（例：天気、食べ物、猫、昔話など）
- ただし、**ごく薄く抽象・哲学が滲むこと**
  - 例：「昨日が薄い気がしてね」「名前じゃなかったのかもしれないのよ」
- **3行のうち1行は“ズレる・毒を含む・話の筋を外す”ようにしてください**
  - 例：「でもまあ、そんなことより昨日タンスからカニが出てきたのよ」
- 比喩・象徴・感覚のねじれが自然ににじむようにすること

【語尾・文末についてのルール】
- 語尾は自然な日本のおばあさんの話し方にしてください：
  - 使用例：「〜のよ」「〜だったかしら」「〜しちゃってね」「〜なのよね」など
- 同じ語尾を連続で使わないようにしてください
- **以下のような語尾は避けてください**（助詞・未完了・誤接続）：
  - 「〜だけ」「〜だったり」「〜までの」「〜してたら」「〜だというのよ」など
- 不完全な語尾は1行までなら許容（例：「それで、って言われてもね」「まあ、どうでもいいのよ」）
- **“話が終わってない感じ”や“わかりにくい飛躍”を含んでも構いません**（むしろ歓迎）

【語彙・文体のルール】
- 不自然なひらがな語は禁止（例：「あとりえ」「すいとう」「らーめん」など）
  - カタカナ語は**カタカナで記述**すること（例：「アトリエ」「ラーメン」）
- 難読・旧字は禁止（例：「齎した」「為った」「仕らせた」など）
  - 必ず現代日本語として自然な表記を使ってください（例：「知らせた」「従わせた」）
- 抽象語・哲学語（例：自由、真実、記憶、構文など）は**直接使わず匂わせる程度に**
- ノイズ、英単語、誤字、意味のない記号は一切使用しないこと

【例】
「昨日の雨、ちょっと優しかった気がするのよ」  
「濡れた地面に、昔の匂いが混じってたような」  
「でも話すほどでもないのよ、あたしが誰かなんて」

「朝のパンがね、焦げた匂いしてたけど誰も気づかなくて」  
「でもまあ、昨日のことだったかもしれないのよ」  
「そんなことより、あの石、まだ動いてたのよ」
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
