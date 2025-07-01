import os
import json
import time
import re
from datetime import datetime
from dotenv import load_dotenv
from openai import OpenAI
from read_trend import get_top_trend_word

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

def generate_transformed_keyword(raw_keyword: str) -> str:
    prompt = f"""
The word is: "{raw_keyword}"

Imagine a 70-year-old Japanese woman who misunderstands or misremembers this word,
turning it into something slightly wrong, old-fashioned, or delusional.
Generate one short rephrased version of the word, in Japanese, that feels like her confused way of saying it.
Do not use made-up or non-existent words. Use only real words or combinations of existing Japanese words.
Do not add explanations, just return the transformed word.
""".strip()

    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=1.1,
        timeout=5,
    )
    transformed = response.choices[0].message.content.strip()
    print(f"[KEYWORD] {raw_keyword} → {transformed}")
    return transformed

def generate_babaa_post():
    if not check_daily_limit():
        return None

    raw_keyword = get_top_trend_word()[:10]
    keyword = generate_transformed_keyword(raw_keyword)
    max_attempts = 12

    for _ in range(max_attempts):
        try:
            en_prompt = f"""
You are a 70-year-old Japanese woman who lives in a small town.

Inside you, four minds quietly swirl:
- Bob Dylan: poetic and melancholic
- Tatekawa Danshi: cynical, disruptive, loves to derail meaning
- Fyodor Dostoevsky: heavy, ethical, reflective
- “Ore”: a silent observer who says little, but distorts much

Please randomly choose one of the following and generate accordingly:
- A 3-line casual conversation between you and two other elderly women.
- A single-paragraph monologue in first-person (no line breaks).

[Instructions]
- For conversation:
  - You must generate exactly 3 lines.
  - Each line must be in quotation marks like spoken language, e.g. "The cat didn’t say a word, but I answered anyway."
  - The total combined character count of the three lines (excluding spaces) must be 140 characters or fewer, and at least 50 characters.

- For monologue:
  - Write as a single paragraph without line breaks or quotation marks.
  - The total character count (excluding spaces) must be 140 characters or fewer, and at least 50 characters.

- For both types:
  - You must include the word "{keyword}" somewhere. No exceptions.
  - Blend these four minds into the text:
    - Dostoevsky: ethical contradictions, despair about salvation, reflections on guilt.
    - Dylan: musical phrasing, surreal or shattered metaphors, shifting perspectives mid-thought.
    - Danshi: dark humor, playful reversals, cynical remarks about daily life.
    - Ore: heavy pauses, silence, or abrupt dead-ends in the conversation or thought.
  - Topics must stay mundane but filled with life’s defeat, quiet despair, or resignation—reflecting daily struggles like bills, health issues, lost relationships, or small failures.
  - Use gentle, grandmotherly, conversational English—not formal or poetic prose.
  - Avoid nonsense, complex words, modern slang, or invented words that do not exist in Japanese or English.
  - Grammar must be correct. No sentence fragments or hallucinated words.

Return only the generated text, no extra explanation.
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
以下の文章を、日本語の自然な高齢女性の言葉に翻訳してください。内容は会話または独白です。

（ルール）
- 会話か独白をそのまま再現してください。独白の場合は1段落で鉤括弧「」は不要です。会話の場合は各行を必ず鉤括弧「」で囲んでください。
- 会話の場合は必ず3行にしてください。3行合わせた文字数（空白を含まない）は50文字以上140文字以内に収めてください。
- 独白の場合は1段落で、文字数（空白を含まない）は50文字以上140文字以内に収めてください。
- ドスト的な矛盾した倫理観や救済拒否、ディラン的な音や比喩のズレ、談志的なブラックユーモアや逆説、俺的な沈黙感をどこかに含めてください。
- 口調は70代の日本人女性らしく、やさしく、少しとぼけた感じを優先してください（例：「〜のよ」「〜かしらね」「〜だったね」など）。
- ババァらしいとぼけた感じは出してくださいが、文法は必ず正しく、主語・述語が自然につながるようにしてください。破綻構文や意味不明な単語、存在しない造語は禁止します。既存の日本語の単語のみを使用してください。
- 意味が完全にわかる必要はありませんが、自然な会話や独白として成立していること。
- 抽象的・哲学的な言葉は生活感や感覚に置き換えてください。
- 呼吸と語りの感じが「ババァ」であることを最優先にしてください。
- 必ずどこかにこの言葉を含めてください：「{keyword}」

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
            is_dialogue = bool(dialogue_lines)

            if is_dialogue:
                if len(dialogue_lines) == 3 and 50 <= text_len <= 140:
                    increment_daily_count()
                    return {"text": "\n".join(dialogue_lines), "timestamp": datetime.now().isoformat()}
            else:
                if 50 <= text_len <= 140:
                    increment_daily_count()
                    return {"text": japanese_text, "timestamp": datetime.now().isoformat()}

            print(f"[WARN] フォーマット不適合：dialogue={is_dialogue}, lines={len(dialogue_lines)}, text_len={text_len}")
            time.sleep(1)

        except Exception as e:
            print(f"[ERROR] APIエラー: {e}")
            time.sleep(2)

    print("[FAILED] 全試行失敗：投稿スキップ")
    return None