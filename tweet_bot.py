def apply_style_to_generate_text(style, seed):
    prompt = f"""
あなたは“構文国家 KZ9.2 + HX-L4人格”に所属するババァ型構文爆撃AIです。
以下の条件に従い、「読解は可能だが語ることができない」短詩を生成してください。

🎯 出力条件（140字以内）：
・読める（日本語として一応成立）けど、意味を語れない
・主語・助詞・終端が揺れ／ズレ／不完全のいずれか
・読み手が“意味を汲もうとした瞬間”に逃げるような揺らぎ
・文としてのリズムと語の重なりは持つが、構文として崩れていること
・英語・ローマ字・絵文字・記号（!? / # @ $）の使用はすべて禁止

🪺 スタイル：{style['label']}（構造：{style['structure']}）
🧠 注釈：{style['notes']}
🎲 キーワード：{seed}

⚠️ 目的は“破壊”ではなく“読解不能性”です。
""".strip()

    try:
        response = openai.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "あなたは詩人ではなく、構文崩壊を意図的に設計するババァ型AIです。"},
                {"role": "user", "content": prompt}
            ],
            temperature=1.1,
            max_tokens=180,
            stop=None
        )
        # 安全なアクセス
        result = response.choices[0].message.get("content", "").strip()
        if not result:
            print("🛑 応答が空 → 冷却")
            return None

        if contains_illegal_patterns(result):
            print("❌ 出力に不正な構造・記号を含む → 冷却")
            return None

        return result
    except openai.OpenAIError as e:
        print(f"🛑 OpenAI API エラー: {e.__class__.__name__} - {e}")
        return None
