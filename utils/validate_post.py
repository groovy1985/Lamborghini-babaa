import re

def is_valid_post(text: str) -> bool:
    """
    validate_post.py｜構文国家：KZHX-L2 準拠検証器

    評価基準：
    - 構文の自然崩壊があること（意味不明ではない）
    - 会話性（応答のように見えるが意味が合っていない）
    - 禁止語・詩語の不使用
    - 過剰な語尾反復・宣言的短文の排除
    """

    if not text or len(text) > 140:
        return False

    lines = [line for line in text.strip().splitlines() if line.strip()]
    if len(lines) != 3:
        return False

    # ❌ 記号・半角・英語・乱数・機械語パターン
    if re.search(r"[a-zA-Z]{4,}", text): return False
    if re.search(r"[^\u3040-\u30FF\u4E00-\u9FFF。、！？「」（）ー…\s]", text): return False
    if re.search(r"[0-9]{4,}", text): return False
    if re.search(r"[a-zA-Z0-9]{6,}", text): return False

    # ❌ 禁止語（意味圧縮・詩語・情動語）
    banned_words = [
        "意味", "感情", "ストーリー", "構文", "主語", "読者", "美しい", "あなたに", "この世界", "物語", "奇跡", "愛",
        "喉", "咳", "希望", "絶望", "輝き", "語尾", "涙", "構成", "時間", "君", "きみ", "記憶", "未来", "大切", "詩"
    ]
    if any(word in text for word in banned_words):
        return False

    # ❌ 過剰な語尾の反復
    if len(re.findall(r"(た|だ|です|ました)[。！？]", text)) >= 3:
        return False

    # ❌ 宣言的短文（CM調コピー）
    if sum(text.count(p) for p in "。！？") <= 1 and len(text) < 40:
        return False

    # ✅ 会話性チェック（応答の構造を最低限満たす）
    reply_hints = ["それで", "やっぱり", "うちも", "たしかに", "でも", "じゃあ", "だから", "のに", "ってこと", "ね", "かも", "よね"]
    if not any(hint in lines[1] for hint in reply_hints) and not any(hint in lines[2] for hint in reply_hints):
        return False

    # ✅ 意味の過剰な連続性を抑制（語彙共有率が高すぎるものを除外）
    def shared_ratio(a, b):
        a_set = set(re.findall(r'\w+', a))
        b_set = set(re.findall(r'\w+', b))
        return len(a_set & b_set) / max(len(a_set), 1)

    if shared_ratio(lines[0], lines[2]) > 0.5:
        return False

    return True
