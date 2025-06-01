import re

def is_valid_post(text: str) -> bool:
    """
    ババァBot用構文爆撃ポスト検証関数（ver.2）
    条件：
    - 140字以内
    - 意味的な語彙・明示的な説明・詩語を含まない
    - 語尾・助詞などの繰り返しを抑止
    - 機械語・乱数・宣言的文体・句点ゼロ短文を除外
    """

    if not text or len(text) > 140:
        return False

    # ❌ 絵文字・半角記号・英語長文・機械語パターン
    if re.search(r"[a-zA-Z]{4,}", text): return False
    if re.search(r"[^\u3040-\u30FF\u4E00-\u9FFF。、！？「」（）ー…\s]", text): return False
    if re.search(r"[0-9]{4,}", text): return False
    if re.search(r"[a-zA-Z0-9]{6,}", text): return False  # 英数字混在の連続は機械語とみなす

    # ❌ 禁止語リスト
    banned_words = [
        "意味", "感情", "ストーリー", "構文", "主語", "読者", "美しい", "あなたに", "この世界", "物語", "奇跡", "愛",
        "喉", "咳", "希望", "絶望", "輝き", "語尾", "涙", "構成", "時間", "君", "きみ", "記憶", "未来", "大切", "詩"
    ]
    for word in banned_words:
        if word in text:
            return False

    # ❌ 「語尾やトーンの同一反復」パターン
    if len(re.findall(r"(た|だ|です|ました)[。！？]", text)) >= 3:
        return False

    # ❌ 短くて完結的な文体（コピーライティングっぽい）
    punctuation_count = sum(text.count(p) for p in "。！？")
    if punctuation_count <= 1 and len(text) < 40:
        return False

    return True
