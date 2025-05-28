def is_reconstructable(text: str) -> bool:
    """
    再構成可能かの粗チェック：
    - 明確な意味のつながりがある
    - 会話文として普通に成立してしまう
    - 要約が容易
    """
    common_phrases = ["つまり", "要するに", "だから", "その結果"]
    if any(phrase in text for phrase in common_phrases):
        return True
    if len(text.split()) < 5:
        return True
    return False


def is_too_meaningful(text: str) -> bool:
    """
    意味性が強すぎる文のフィルター
    """
    direct_meanings = ["人生", "愛", "正義", "自由", "希望"]
    return any(word in text for word in direct_meanings)


def is_valid_post(text: str) -> bool:
    """
    再構成性や意味過多を含むポストを排除
    """
    if is_reconstructable(text):
        return False
    if is_too_meaningful(text):
        return False
    return True
