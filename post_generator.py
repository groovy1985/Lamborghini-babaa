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
            print(f"\u26d1\ufe0f \u672c\u65e5\u5206\u306e\u751f\u6210\u4e0a\u9650\uff08{DAILY_LIMIT}\u4ef6\uff09\u306b\u9054\u3057\u307e\u3057\u305f")
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
        json.dump(data, f, ensure_ascii=False, indent=2)

def generate_babaa_post():
    if not check_daily_limit():
        return None

    max_attempts = 10
    for _ in range(max_attempts):
        try:
            jp_prompt = """
老女二人による三行の会話を書いてください。

各行は、前の発言に“応答しているように見える”必要がありますが、意味内容は微妙にずれていてください。
応答のように見せかけながら、認識のすれ違いや比喩的な脱線が起こるようにしてください。

会話は、かろうじて整合しているように振る舞いながら、静かにその一貫性が崩れていくものにしてください。
完全に意味不明にならないようにしてください。詩的で構造が壊れているように見えても、意図的な会話形式でなければいけません。

感傷的・抽象的な単語（愛・希望・記憶・魂など）は避けてください。
名前・話者記号は使わず、日本語の会話文のように「」で始まる3行で書いてください。
それぞれの行は、独立した比喩や印象を持ちつつ、会話全体が“幽霊同士の誤解”のように見えるようにしてください。

例：
「昨日、納屋で赤ん坊みたいな音を聞いたの」
「うちも、階段の影が時々喋るって言ってたわ」
「でも靴だけは、もう誰にも履かせないんだって」
"""

            response = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": jp_prompt.strip()}],
                temperature=1.25,
            )
            japanese_text = response.choices[0].message.content.strip()
            print(f"\ud835\udd38 JP: {japanese_text}")

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
                print(f"\u26a0\ufe0f \u884c\u6570\u307e\u305f\u306f\u9577\u3055\u4e0d\u9069\u5207\uff08{len(lines)}\u884c\uff0f{total_len}\u5b57\uff09\u2192 \u30b9\u30ad\u30c3\u30d7")
                time.sleep(1)

        except Exception as e:
            print(f"\u274c API\u30a8\u30e9\u30fc: {e}")
            time.sleep(2)

    print("\ud83d\udeab \u5168\u8a66\u884c\u5931\u6557\uff1a\u6295\u7a3f\u30b9\u30ad\u30c3\u30d7")
    return None
