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
