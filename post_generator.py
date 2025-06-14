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
以下の条件で、日本語の構文崩壊型テキストを生成してください。

【バリエーション分岐】
・文数はランダムで2〜4文としてください
・文が2〜4行の場合 → 会話文形式（各文を「」で囲んでください）
・文が1文の場合 → 独白形式（「」なしで、地の文として書いてください）

【語尾仕様】
・語尾は60〜70代の女性が話しそうな自然な口語調としてください（例：「〜だったかしら」「〜なんじゃないの」「〜しちゃったのよ」「〜ってさあ」など）
・3文以上の場合は語尾のスタイルを必ず変えてください（毎文同じ「〜のよ」はNG）
・「〜わ」「〜かしら」など**既視感の強い語尾は禁止**

【内容】
・社会制度や生活実感が反映された現実的な語彙（例：通帳、ガス代、病院、年金、スマホ、地域ポイント、タクシー券、テレビ、漬物石など）を用いてください
・ただし意味は連鎖させず、会話／独白が少しズレた状態を維持してください
・比喩や例えは雑でOKですが、**文脈にうまく収まらないようにしてください**
・誰が誰に話しているのかわからない構文になることを目指してください

【禁止事項】
・愛、希望、記憶、救い、夢、自由などの抽象語は禁止
・登場人物名、時制がはっきりした話、オチのある話は禁止
・構文全体が意味をもって「理解できる」ようにしないでください

【出力形式】
・2〜4文：各文を「」で囲んで会話形式にしてください
・1文：地の文として書いてください（「」は禁止）
・全体で140文字以内にしてください

"""

            response = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": jp_prompt.strip()}],
                temperature=1.25,
                timeout=15,
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
