import re

def is_valid_post(text: str) -> bool:
    """
    ズレた会話文を許容する軽量チェック：
    ・構文語／論理語／明確な結論を避ける
    ・詩や演説になりすぎたものは冷却
    """

    # NGワード（説明語・結論・文法語など）
    banned_keywords = [
        "つまり", "なぜなら", "要するに", "結局", "構文", "主語", "語尾", "論理", "理由", "定義"
    ]

    # 英語・記号・短すぎる文字列は不可（ただし改行は許容）
    if re.search(r"[a-zA-Z]{3,}", text):
        return False
    if re.search(r"[^\u3040-\u30FF\u4E00-\u9FFF。、！？「」ーぁ-んァ-ン0-9\n\s]", text):
        return False
    if len(text.strip()) < 15:
        return False

    # 明らかに詩構造になってるもの（行頭繰り返しや句読点連続）を排除
    if text.count("。") > 5 or text.count("、") > 7:
        return False
    if re.search(r"(あたし|でも|ねえ|それで|まあ|だから|さては)", text[:10]) is None:
        return False  # 会話文らしい出だしでなければ冷却

    # NGワード含むなら即冷却
    for kw in banned_keywords:
        if kw in text:
            return False

    return True
