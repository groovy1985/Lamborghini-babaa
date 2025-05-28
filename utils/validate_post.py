import re

def is_reconstructable(text: str) -> bool:
    """
    再構成可能かの強化判定：
    - 明確な因果・文脈がある
    - 話し言葉として流れが自然すぎる
    - 読後に説明できてしまう
    """
    common_phrases = ["つまり", "そのため", "だから", "ようするに", "結果として", "要するに"]
    if any(phrase in text for phrase in common_phrases):
        return True
    if re.match(r"^「.*」$", text) or text.endswith("と思う。"):
        return True
    if len(text.split()) < 5 and "。" in text:
        return True
    return False


def is_too_meaningful(text: str) -> bool:
    """
    意味語フィルター：Botが“理解”してしまう語を含むと即落選
    """
    direct_meanings = ["人生", "愛", "正義", "希望", "自由", "平和", "戦争", "信じる", "未来"]
    return any(word in text for word in direct_meanings)


def has_repetitive_phrases(text: str) -> bool:
    """
    語尾や句構造の反復チェック（3回以上）
    """
    endings = re.findall(r"[ぁ-んァ-ンーa-zA-Z]+[。．…!?]?", text)
    for end in set(endings):
        if end and text.count(end) >= 3:
            return True
    return False


def uses_prohibited_terms(text: str) -> bool:
    """
    禁止語（構文語など）が含まれるか
    """
    banned = ["構文", "語尾", "主語", "文法", "読点", "句点", "意味", "AI"]
    return any(word in text for word in banned)


def is_valid_post(text: str) -> bool:
    """
    最終フィルター：KZ9.2 + HX-L4人格による冷却判定
    """
    if is_reconstructable(text):
        print("❌ 再構成可能 → 冷却")
        return False
    if is_too_meaningful(text):
        print("❌ 意味化された語彙を含む → 冷却")
        return False
    if has_repetitive_phrases(text):
        print("❌ 語法の反復あり → 冷却")
        return False
    if uses_prohibited_terms(text):
        print("❌ 構文語の使用 → 冷却")
        return False
    return True
