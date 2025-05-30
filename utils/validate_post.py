import re

def is_valid_post(text: str) -> bool:
    """
    ババァBot用構文爆撃ポストの検証関数。
    条件：
    - 140字以内
    - 説明文・詩文・コピー文でない
    - 構文の揺れ・ズレが内在
    - 禁止語・記号・語尾連続を含まない
    """

    if not text or len(text) > 140:
        return False

    # ❌ 禁止文字・記号（絵文字や機械語、アルファベット長文、特殊記号など）
    if re.search(r"[a-zA-Z]{4,}", text): return False
    if re.search(r"[^\u3040-\u30FF\u4E00-\u9FFF。、！？「」（）ー…\s]", text): return False

    # ❌ 禁止語彙（明示的な意味構造や説明語、詩的単語）
    banned_words = [
        "意味", "感情", "ストーリー", "構文", "主語", "読者", "美しい", "あなたに", "この世界", "物語", "奇跡", "愛",
        "喉", "咳", "希望", "絶望", "輝き", "語尾", "涙", "構成", "時間", "君", "きみ", "記憶", "未来", "大切", "詩"
    ]
    for word in banned_words:
        if word in text:
            return False

    # ❌ 語尾・助詞連続（〜た。〜た。〜た。など3回以上）
    if len(re.findall(r"た[。！？]", text)) >= 3: return False
    if len(re.findall(r"です[。！？]", text)) >= 3: return False
    if len(re.findall(r"だ[。！？]", text)) >= 3: return False

    # ❌ 完結的な宣言・キャッチコピー系文体（句読点1つ以下 or トーンが均質）
    if text.count("。") + text.count("！") + text.count("？") <= 1:
        if len(text) < 40:  # 短くて明快な文は冷却
            return False

    # ✅ ここまで来たら基本OK
    return True
