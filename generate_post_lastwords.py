import os
import sys
from openai import OpenAI
from tweet_bot import tweet_post  # ✅ ここ追加

# ✅ APIクライアントの初期化
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ✅ ババァ吊構文プロンプト（完全再現）
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

# ✅ ババァ会話生成関数（プロンプト直流し）
def generate_babaa_post(trigger_text: str = "") -> str:
    res = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": jp_prompt.strip()}],
        temperature=1.3,
    )
    return res.choices[0].message.content.strip()

# ✅ メイン処理（GitHub Actionsから呼び出される）
if __name__ == "__main__":
    repo = sys.argv[1] if len(sys.argv) > 1 else "Last-Words-Archive"
    trigger = sys.argv[2] if len(sys.argv) > 2 else "default"

    print(f"🧙‍♀️ Triggered by {repo} with event '{trigger}'")
    result = generate_babaa_post()
    print("📝 Generated Babaa Post:\n")
    print(result)

    # 保存（オプション）
    os.makedirs("output", exist_ok=True)
    with open("output/babaa_generated.txt", "w", encoding="utf-8") as f:
        f.write(result)

    # ✅ 投稿（Tweet）実行
    tweet_post(result)
