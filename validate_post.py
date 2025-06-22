import re

def is_valid_post(text: str) -> bool:
    """
    validate_post.py｜構文国家：KZHX-L4.1 準拠検証器（ver.1.1）
    - GPT語尾破綻・構文崩壊・意味逸脱の中間ゾーンを精密に選別
    """

    if not text or not (20 <= len(text) <= 140):
        return False

    # 各行抽出
    lines = [line.strip() for line in text.strip().splitlines() if line.strip()]
    if len(lines) != 3:
        return False

    # 「」で囲まれているか
    if not all(line.startswith("「") and line.endswith("」") for line in lines):
        return False

    # ノイズ英数字列
    if re.search(r"[a-zA-Z]{4,}", text): return False
    if re.search(r"[0-9]{5,}", text): return False
    if re.search(r"[a-zA-Z0-9]{6,}", text): return False

    # 異体字・中国簡体字等
    if re.search(r"[锕鱻靐靇㐀-㛿㐂-㊿㋿㐧䲣]", text): return False

    # 記号チェック
    if re.search(r"[^\u3040-\u30FF\u4E00-\u9FFF。、！？「」（）ー…％：/\-\s]", text):
        return False

    # 禁止語
    banned_words = ["構文", "主語", "美しい", "物語", "語尾", "構成"]
    if any(word in text for word in banned_words):
        return False

    # 過剰な文末反復
    if len(re.findall(r"(た|だ|です|ました)[。！？]", text)) == 3:
        return False

    # CM的短文
    if sum(text.count(p) for p in "。！？") <= 1 and len(text) < 40:
        return False

    # 応答擬態
    reply_hints = ["それで", "やっぱり", "うちも", "たしかに", "でも", "じゃあ", "だから", "のに", "ってこと", "ね", "かも", "よね"]
    if not any(hint in lines[1] for hint in reply_hints) and not any(hint in lines[2] for hint in reply_hints):
        return False

    # 不自然語尾検知（ver.1.1）
    unnatural_ending_patterns = [
        r"ではや$", r"だよよ$", r"のかの$", r"でしょうの$", r"なんだがよ$",
        r"だったがよ$", r"らしいけどよ$", r"だったよなぁ$", r"ではか$",
        r"だというのよ$", r"ますことよ$", r"たというわよ$", r"みたいでしたわ$", r"でしてたのよ$"
    ]
    def has_unnatural_ending(line: str) -> bool:
        return any(re.search(pat, line) for pat in unnatural_ending_patterns)
    if any(has_unnatural_ending(line) for line in lines):
        return False

    # 過剰語彙一致（反復構文の検出）
    def shared_ratio(a, b):
        a_set = set(re.findall(r'[\u3040-\u30FF\u4E00-\u9FFF]+', a))
        b_set = set(re.findall(r'[\u3040-\u30FF\u4E00-\u9FFF]+', b))
        return len(a_set & b_set) / max(len(a_set), 1)
    if shared_ratio(lines[0], lines[2]) > 0.7:
        return False

    return True
