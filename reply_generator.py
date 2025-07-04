import os
import json
import time
import re
from datetime import datetime
from dotenv import load_dotenv
from openai import OpenAI

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

def extract_keyword_from_text(text):
    keywords = re.findall(r'[一-龯]{2,}|[ァ-ヶー]{2,}', text)
    if keywords:
        print(f"[INFO] 抽出キーワード: {keywords[0]}")
        return keywords[0]
    return "思い出"  # fallback

def generate_babaa_reply(context_text):
    if not check_daily_limit():
        return None

    keyword = extract_keyword_from_text(context_text)[:10]
    max_attempts = 12

    for _ in range(max_attempts):
        try:
            en_prompt = f"""
You are a 70-year-old Japanese woman living in a small town.

Generate a 3-line conversation between you and two elderly women reacting indirectly to this tweet:
"{context_text}"

[Instructions]
- Each line must be in quotation marks like spoken language, e.g. "The cat didn’t say a word, but I answered anyway."
- Output exactly 3 lines.
- Total combined character count (excluding spaces) should be under 280.
- Include the word "{keyword}" in at least one line.
- Each line must contain a Dylan-like random metaphor or surreal image, something unexpected or disconnected from reality.
- Each line should feel like it almost makes sense but carries a subtle dissonance or ambiguity, as if meaning slips away on closer look.
- Let each line carry hints of defeat, resignation, and oddly wise phrasing, but with subtle disjointedness so they don’t fully connect.
- Avoid personal names, nonsense words, or modern slang.
- Use gentle, grandmotherly, conversational English—not formal prose.
- Grammar must be correct; avoid sentence fragments or hallucinated words.

Return only the 3 lines, no extra explanation.
""".strip()

            response = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": en_prompt}],
                temperature=1.2,
                timeout=10,
            )
            english_text = response.choices[0].message.content.strip()
            print(f"[EN] {english_text}")

            translate_prompt = f"""
次の英語の3行会話を日本語の自然な高齢女性の会話に翻訳してください。

[ルール]
- 各行は「」で囲んでください。
- 各行内で引用や印象的な単語は『』を使って強調してください。
- 出力は必ず3行。
- 総文字数は50〜145文字以内にしてください。
- 個人名・固有名詞は禁止。
- ババァらしいとぼけた口調にしつつ文法は正しく。
- 各行は成立しているようで微妙にかみ合わないズレを含めてください。
- 同じ語尾（〜のよ、〜だわ、〜ねなど）を複数行で繰り返さないでください。3行とも異なる語尾にしてください。
- 各行には必ず現実離れした唐突なメタファーやイメージ（Dylan的ズラし）を含め、意味がかみ合いそうでかみ合わないようにしてください。
- 哲学的表現は生活感に置き換え、自然な会話にしてください。
- 必ず1行に「{keyword}」を含めてください。

翻訳対象:
{english_text}
""".strip()

            translation = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": translate_prompt}],
                temperature=1.0,
                timeout=15,
            )
            japanese_text = translation.choices[0].message.content.strip()
            print(f"[JP] {japanese_text}")

            dialogue_lines = re.findall(r'「.*?」', japanese_text, re.DOTALL)
            text_len = len(re.sub(r'\s', '', japanese_text))

            if len(dialogue_lines) == 3 and 50 <= text_len <= 145:
                increment_daily_count()
                return {"text": "\n".join(dialogue_lines), "timestamp": datetime.now().isoformat()}

            print(f"[WARN] フォーマット不適合：lines={len(dialogue_lines)}, text_len={text_len}")
            time.sleep(1)

        except Exception as e:
            print(f"[ERROR] APIエラー: {e}")
            time.sleep(2)

    print("[FAILED] 全試行失敗：投稿スキップ")
    return None
