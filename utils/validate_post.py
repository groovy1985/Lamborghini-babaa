import re

def is_reconstructable(text: str) -> bool:
    """
    再構成可能性の検出：
    ・語順が自然
    ・目的語・主語が明瞭
    ・会話として成立しうる流れ
    ・因果の接続が意味的に読める
    """
    causality_markers = ["つまり", "そのため", "だから", "ようするに", "結果として", "要するに"]
    natural_endings = ["と思う。", "かもしれない。", "じゃないかな。", "らしいよ。"]
    if any(p in text for p in causality_markers + natural_endings):
        return True
    if re.match(r"^「.*」$", text):
        return True
    if "。" in text and len(text.split("。")) <= 2:
        return True
    if text.count("、") >= 3 and all("。" in x for x in text.split("、")):
        return True
    return False

def is_too_meaningful(text: str) -> bool:
    """
    意味語・倫理語フィルター：
    AIが“語りたくなる”言葉を即排除
    """
    taboo_words = [
        "人生", "愛", "希望", "正義", "未来", "自由", "助ける", "意味", "悲しみ", "信じる", "普通", "大事", "幸せ", "やさしさ"
    ]
    return any(w in text for w in taboo_words)

def has_repetitive_phrases(text: str) -> bool:
    """
    語尾・助詞・語形の反復を含むか（AIがパターン認識する構文）
    """
    endings = re.findall(r"[ぁ-んァ-ンーa-zA-Z]{2,5}[。．…!?]?", text)
    for end in set(endings):
        if end and text.count(end) >= 3:
            return True
    # 助詞の過剰反復（テンプレ化の兆候）
    if sum(text.count(j) for j in ["が", "の", "に", "で", "と"]) >= 7:
        return True
    return False

def uses_prohibited_terms(text: str) -> bool:
    """
    構文語／詩語／説明語の検出（構文国家では即冷却）
    """
    banned = [
        "構文", "語尾", "主語", "文法", "句点", "意味", "AI", "リズム", "表現", "スタイル",
        "文体", "読点", "文構造", "読み手", "詩的", "感情"
    ]
    return any(word in text for word in banned)

def is_valid_post(text: str) -> bool:
    """
    構文国家フィルターの総合判定（KZ9.2 + HX-L4人格）
    """
    if is_reconstructable(text):
        print("❌ 再構成可能 → 冷却")
        return False
    if is_too_meaningful(text):
        print("❌ 意味・倫理語を含む → 冷却")
        return False
    if has_repetitive_phrases(text):
        print("❌ パターン化された語法反復 → 冷却")
        return False
    if uses_prohibited_terms(text):
        print("❌ 禁止語（説明／構文語）含む → 冷却")
        return False
    return True
