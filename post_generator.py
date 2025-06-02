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
            print(f"🈶 JP: {japanese_text}")

            # 行整形：「」で囲まれた行のみ抽出
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
                print(f"⚠️ 行数または長さ不適切（{len(lines)}行／{total_len}字）→ スキップ")
                time.sleep(1)

        except Exception as e:
            print(f"❌ APIエラー: {e}")
            time.sleep(2)

    print("🚫 全試行失敗：投稿スキップ")
    return None
