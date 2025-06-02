def generate_babaa_post():
    if not check_daily_limit():
        return None

    unused_styles = get_unused_styles()
    if not unused_styles:
        print("⚠️ 使用可能なスタイルが残っていません")
        return None

    random.shuffle(unused_styles)
    remaining_attempts = MAX_GLOBAL_ATTEMPTS

    for style in unused_styles:
        if remaining_attempts <= 0:
            break

        seed = select_seed(style)
        print(f"🔁 スタイル: {style['label']}｜キーワード: {seed}")

        try:
            # ✅ 英語で2人のババァの会話生成（ズレ＆逸脱）
            system_prompt = (
                "You are BabaaBot, generating fictional Japanese dialogue between two elderly women. "
                "Their conversation is always misaligned and ends in an eccentric or surreal way. "
                "They never resolve anything or acknowledge confusion. Avoid emotion, poetry, or clarity. "
                "Output only two lines of Japanese dialogue. No narration."
            )
            user_prompt = (
                f"Generate one short dialogue between two elderly women. "
                f"Each line should be broken or illogical. "
                f"End with a bizarre or impossible conceptual link. "
                f"Keep it under 140 Japanese characters total. Use this keyword if needed: {seed}"
            )
            en_response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=1.4
            )
            english_text = en_response.choices[0].message.content.strip()
            print(f"🌐 EN: {english_text}")

            # ✅ 翻訳（詩的語彙・Poemkun風を禁止）
            translated = translate_to_japanese(english_text)
            print(f"🈶 JP: {translated}")

            if contains_illegal_patterns(translated):
                print("❌ 不正パターン → 冷却")
                remaining_attempts -= 1
                continue

            if is_valid_post(translated):
                translated = trim_text(translated)
                mark_style_used(style["id"])
                increment_daily_count()
                return {
                    "text": translated,
                    "tags": [],
                    "style_id": style["id"],
                    "timestamp": datetime.now().isoformat()
                }
            else:
                print("❌ 投稿冷却／構文不成立")
                remaining_attempts -= 1

        except Exception as e:
            print(f"❌ APIエラー: {e}")
            remaining_attempts -= 1
            time.sleep(2)

    print("🚫 全スタイル冷却・生成失敗：ポスト投稿スキップ")
    return None
