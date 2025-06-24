import re
import time
from datetime import datetime
from read_trend import get_japan_trends

import openai
client = openai  # ← これを忘れてた

def generate_babaa_post():
    # ✅ トレンド語の取得（先頭1つだけ使用）
    try:
        trends = get_japan_trends()
        keyword = trends[0] if trends else "お味噌汁"
    except Exception as e:
        print(f"[WARN] トレンド取得失敗: {e}")
        keyword = "お味噌汁"

    print(f"[TREND] 今日のトレンド語: {keyword}")

    max_attempts = 10
    for _ in range(max_attempts):
        try:
            en_prompt = f"""
You are a 70-year-old Japanese woman who lives in a small town.

Inside you, four minds quietly swirl:
- Bob Dylan: poetic and melancholic
- Tatekawa Danshi: cynical, disruptive, loves to derail meaning
- Fyodor Dostoevsky: heavy, ethical, reflective
- “Ore”: a silent observer who says little, but distorts much

Please generate a 3-line casual conversation between you and two other elderly women.
You're chatting by the roadside. It should feel like soft gossip mixed with strange thoughts.

[Instructions]
- Output must be exactly 3 lines.
- Each line should be in quotation marks, like spoken language. E.g. "The cat didn’t say a word, but I answered anyway."
- Keep topics mundane (e.g. tofu, laundry, birds), but let each line carry a faint twist—philosophical, surreal, or emotionally ambiguous.
- Use gentle, grandmotherly, conversational English—not formal, not poetic prose.
- Grammar must be correct. No sentence fragments or hallucinated words.
- Total output must stay under 280 characters.
- **Use the word "{keyword}" naturally in at least one line.**

Return only the 3 quoted lines, no extra explanation.
""".strip()

            response = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": en_prompt}],
                temperature=1.2,
                timeout=15,
            )
            english_text = response.choices[0].message.content.strip()
            print(f"[EN] {english_text}")

            translate_prompt = f"""
以下の3行の英語の発言を、日本語の自然な高齢女性の会話文に翻訳してください。

（ルール）
- 口調は70代の日本人女性らしく、やさしく、すこしとぼけた口調にしてください（例：「〜のよ」「〜かしらね」「〜だったね」など）
- 文法は必ず成立させ、破繕構文や意味不明な語彙は禁止します
- 意味がわかりすぎる必要はありませんが、会話として自然に聞こえること
- 各行は必ず日本語の鎩括括「」で囲んでください
- 抽象語・哲学語はそのまま翻訳せず、生活感や感覚に置き換えてください
- 形式ではなく、呼吸と語りの感じが“ババァ”であることを最優先にしてください
- 必ずどこかの1行にこの言葉を含めてください：「{keyword}」

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
                if 1 <= len(dialogue_lines) <= 4 and text_len <= 140:
                    return {"text": "\n".join(dialogue_lines), "timestamp": datetime.now().isoformat()}
            else:
                if 1 <= text_len <= 140:
                    return {"text": japanese_text, "timestamp": datetime.now().isoformat()}

            print(f"[WARN] フォーマット不適合：dialogue={is_dialogue}, lines={len(dialogue_lines)}, text_len={text_len}")
            time.sleep(1)

        except Exception as e:
            print(f"[ERROR] APIエラー: {e}")
            time.sleep(2)

    print("[FAILED] 全試行失敗：投稿スキップ")
    return None
