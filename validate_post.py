import re

def is_valid_post(text: str) -> bool:
    """
    validate_post.py｜構文国家：KZHX-L4 準拠検証器
    """

    if not text or not (20 <= len(text) <= 140):
        return False

    lines = [line.strip() for line in text.strip().splitlines() if line.strip()]
    if len(lines) != 3:
        return False

    # ✅ 日本語の会話形式であるか（「」で囲まれている）
    if not all(line.startswith("「") and line.endswith("」") for line in lines):
        return False

    # ❌ 英数字・ノイズ記号・4桁以上の数値・長いランダム列
    if re.search(r"[a-zA-Z]{4,}", text): return False
    if re.search(r"[^\u3040-\u30FF\u4E00-\u9FFF。、！？「」（）ー…\s]", text): return False
    if re.search(r"[0-9]{4,}", text): return False
    if re.search(r"[a-zA-Z0-9]{6,}", text): return False

    # ❌ 詩語・情動語・構文用語など意味圧縮語
    banned_words = [
        "意味", "感情", "ストーリー", "構文", "主語", "読者", "美しい", "あなたに", "この世界", "物語", "奇跡", "愛",
        "喉", "咳", "希望", "絶望", "輝き", "語尾", "涙", "構成", "時間", "君", "きみ", "記憶", "未来", "大切", "詩",
        "存在", "運命", "永遠", "真実", "境界", "命", "魂", "祈り", "孤独"
    ]
    if any(word in text for word in banned_words):
        return False

    # ❌ 文末表現の冗長性チェック（〜た。〜た。〜た。等）
    if len(re.findall(r"(た|だ|です|ました)[。！？]", text)) >= 3:
        return False

    # ❌ 短すぎる宣言文（CM調コピー）
    if sum(text.count(p) for p in "。！？") <= 1 and len(text) < 40:
        return False

    # ✅ 会話ズレ応答の判定（2行目or3行目に最低1つ）
    reply_hints = ["それで", "やっぱり", "うちも", "たしかに", "でも", "じゃあ", "だから", "のに", "ってこと", "ね", "かも", "よね"]
    if not any(hint in lines[1] for hint in reply_hints) and not any(hint in lines[2] for hint in reply_hints):
        return False

    # ❌ 過剰な語彙一致（吊れてない循環会話除外）
    def shared_ratio(a, b):
        a_set = set(re.findall(r'[\u3040-\u30FF\u4E00-\u9FFF]+', a))
        b_set = set(re.findall(r'[\u3040-\u30FF\u4E00-\u9FFF]+', b))
        return len(a_set & b_set) / max(len(a_set), 1)

    if shared_ratio(lines[0], lines[2]) > 0.5:
        return False

    return True
