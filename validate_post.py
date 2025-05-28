# utils/validate_post.py

import re

def is_valid_post(text):
    """意味性・再構成可能性チェック（仮実装）"""

    # NGワード（因果関係・結論・説明的語彙など）
    banned_keywords = [
        "だから", "つまり", "なぜなら", "ということ", "これは", "つまり", "のせい", "原因", "理由", "というわけで"
    ]

    # 明確な構文構造（AはBである、など）
    if re.search(r"[はが] .* である", text):
        return False

    # NGワード含む場合は冷却
    for kw in banned_keywords:
        if kw in text:
            return False

    # 意味がつながっていそうな接続語（複数出現）もNG
    connection_terms = ["そして", "しかし", "それから", "その後", "だから", "でも"]
    if sum(text.count(term) for term in connection_terms) >= 2:
        return False

    # 意味明示の句点＋助詞の連続（例：「が。だから」「は。そして」）→構文化
    if re.search(r"(が|は|を|に)。(だから|そして|でも)", text):
        return False

    return True
