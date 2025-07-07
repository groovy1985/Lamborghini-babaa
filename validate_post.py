import re

def is_valid_monologue(text: str) -> bool:
    """
    validate_post.py｜構文国家：KZHX-L4.2 独白専用検証器（ver.1.3独白版）
    - GPT語尾破綻・構文崩壊・意味逸脱の中間ゾーンを精密に選別
    - 独白（1段落・鉤括弧なし）のみを許容する
    """

    if not text or not (20 <= len(text) <= 140):
        # 20文字未満または140文字超過は無効
        return False

    line = text.strip()

    # 独白：鉤括弧が含まれていないこと
    if "「" in line or "」" in line:
        return False

    # 英数字4文字以上連続はGPT由来ノイズと判断して排除
    if re.search(r"[a-zA-Z0-9]{4,}", text):
        return False

    # 異体字・簡体字など、異常漢字の混入チェック
    if re.search(r"[锕鱻靐靇㐀-㛿㐂-㊿㋿㐧䲣]", text):
        return False

    # 記号チェック：日本語で通常使わない記号を排除
    if re.search(r"[^\u3040-\u30FF\u4E00-\u9FFF。、！？ー…％：/\-\s]", text):
        return False

    # 禁止語：構文国家内で構造記述に該当し不自然さを生む単語
    banned_words = ["構文", "主語", "語尾", "構成"]
    if any(word in text for word in banned_words):
        return False

    # 不自然な文末パターン：GPTの典型的な語尾破綻
    unnatural_ending_patterns = [
        r"ではや$", r"だよよ$", r"のかの$", r"でしょうの$", r"なんだがよ$",
        r"だったがよ$", r"らしいけどよ$", r"だったよなぁ$", r"ではか$",
        r"だというのよ$", r"ますことよ$", r"たというわよ$", r"みたいでしたわ$", r"でしてたのよ$"
    ]
    if any(re.search(pat, line) for pat in unnatural_ending_patterns):
        return False

    return True