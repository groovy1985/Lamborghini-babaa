import re

def is_valid_post(text: str) -> bool:
    """
    validate_post.py｜構文国家：KZHX-L4.1 準拠検証器（哲学語・抽象語の直言を一部許容）
    """

    if not text or not (20 <= len(text) <= 140):
        return False

    lines = [line.strip() for line in text.strip().splitlines() if line.strip()]
    if len(lines) != 3:
        return False

    if not all(line.startswith("「") and line.endswith("」") for line in lines):
        return False

    # ❌ ノイズ英数字列（明らかな乱数・ランダム英語）
    if re.search(r"[a-zA-Z]{4,}", text): return False
    if re.search(r"[0-9]{5,}", text): return False
    if re.search(r"[a-zA-Z0-9]{6,}", text): return False

    # ⚠️ 記号制限（日本語会話で自然な範囲のみ許容）
    if re.search(r"[^\u3040-\u30FF\u4E00-\u9FFF。、！？「」（）ー…％：/\-\s]", text):
        return False

    # ❌ 禁止語（美化・感動・説明臭・テーマ語系）※哲学語・抽象語は緩和済
    banned_words = [
         "構文", "主語", "美しい", 
         "物語", "語尾", 
        "構成",
    ]
    if any(word in text for word in banned_words):
        return False

    # ❌ 文末の過剰反復（リズム崩壊の防止）
    if len(re.findall(r"(た|だ|です|ました)[。！？]", text)) == 3:
        return False

    # ❌ CM的短文（意味性の固定化を避ける）
    if sum(text.count(p) for p in "。！？") <= 1 and len(text) < 40:
        return False

    # ✅ 応答構造の擬態確認（対話らしさの担保）
    reply_hints = ["それで", "やっぱり", "うちも", "たしかに", "でも", "じゃあ", "だから", "のに", "ってこと", "ね", "かも", "よね"]
    if not any(hint in lines[1] for hint in reply_hints) and not any(hint in lines[2] for hint in reply_hints):
        return False

    # ❌ 過剰な語彙一致の防止（反復構文のバグ対策）
    def shared_ratio(a, b):
        a_set = set(re.findall(r'[\u3040-\u30FF\u4E00-\u9FFF]+', a))
        b_set = set(re.findall(r'[\u3040-\u30FF\u4E00-\u9FFF]+', b))
        return len(a_set & b_set) / max(len(a_set), 1)

    if shared_ratio(lines[0], lines[2]) > 0.7:
        return False

    return True
