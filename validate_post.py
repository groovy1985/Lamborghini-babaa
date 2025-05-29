import re

def is_valid_post(text):
    """意味性・再構成可能性チェック（強化版）"""

    banned_keywords = [
        "だから", "つまり", "なぜなら", "ということ", "これは", "のせい", "原因", "理由", "というわけで"
    ]

    connection_terms = [
        "そして", "しかし", "それから", "その後", "だから", "でも",
        "また", "一方で", "なお", "ちなみに", "そのため", "とはいえ"
    ]

    # NGキーワード含む → 冷却
    for kw in banned_keywords:
        if kw in text:
            return False

    # 明示的構造（主語＋述語） → 冷却
    if re.search(r".+[はがを] .+(です|である|でした|だ)$", text):
        return False

    # 接続詞多用（2つ以上） → 冷却
    if sum(text.count(term) for term in connection_terms) >= 2:
        return False

    # 助詞＋句点＋接続詞 → 冷却
    if re.search(r"(が|は|を|に)。(だから|そして|でも|また)", text):
        return False

    # 文末が説明的 → 冷却
    if re.search(r"(です|ます|である)。", text):
        return False

    return True
