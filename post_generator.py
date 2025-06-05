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
老女三人による三行の会話を生成してください。

・各行は、まるで応答しているように“見える”必要がありますが、実際には意味がずれていること。
・1行目は自然で平和な観察、2行目はそれに対するズレた応答、3行目は空気を壊すような倫理的・構文的逸脱で終えること。
・語尾は「〜わ」「〜のよ」「〜かしら」などで統一しますが、1文だけ故意に語尾を崩して構いません（例：「〜さ」「〜んだってね」など）。
・老女たちは互いに張り合いながらも、どこかで死・孤独・過去の記憶・倫理の解体を含んだ発言をするようにしてください。
・言葉の構文は吊られていても意味は読み取れるようにし、「崩壊しているが再構成できる会話」にしてください。
・愛・希望・記憶・魂などの抽象語は禁止です。名前・記号も使用しないでください。

例：
「昨日、納屋で赤ん坊みたいな音を聞いたのよ」
「うちも、階段の影が時々喋るって言ってたわ」
「でも靴だけは、もう誰にも履かせないんだってさ」
"""

            response = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": jp_prompt.strip()}],
                temperature=1.5,
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
