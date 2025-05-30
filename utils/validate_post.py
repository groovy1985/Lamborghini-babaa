import re

def is_valid_post(text: str) -> bool:
    """
    ババァ構文検閲フィルター
    読めるが語れない文のみを通過させる。
    """

    if not text or len(text.strip()) < 15:
        print("❌ テキストが短すぎる")
        return False

    # NGワード：明確な論理接続・説明語・正論
    banned_words = [
        "だから", "つまり", "なぜなら", "理由は", "要するに", "ということ", "それゆえ", "である", "ですが", "ます", "ました", "と思います"
    ]
    for word in banned_words:
        if word in text:
            print(f"❌ 意味化ワード検出: {word}")
            return False

    # 接続詞が2つ以上出ると、文脈が生まれやすい
    connectors = ["そして", "しかし", "それから", "その後", "でも"]
    if sum(text.count(w) for w in connectors) > 1:
        print("❌ 接続語の多用 → 構文成立疑い")
        return False

    # AはBである構文
    if re.search(r"[はが] .*である", text):
        print("❌ 形式構文（AはBである）検出")
        return False

    # 明瞭な因果構造：「○○。だから〜」「○○、それで〜」など
    if re.search(r"(。|、)(だから|それで|ゆえに|なので)", text):
        print("❌ 因果接続で構文が閉じている")
        return False

    # あまりにきれいすぎる文末（明確な文・説明・感想）
    if re.search(r"(です|ます|でした|と思います)$", text):
        print("❌ 文末がきれいに閉じている")
        return False

    # 語尾・助詞の反復（テンプレ的リズム）
    endings = re.findall(r"[ぁ-んァ-ンー]+", text)
    for word in set(endings):
        if text.count(word) >= 3 and len(word) > 1:
            print(f"❌ 語尾反復検出: {word}")
            return False

    return True
