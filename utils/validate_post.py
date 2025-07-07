import re

def is_valid_monologue(text: str) -> bool:
    """
    validate_post.py｜構文国家：KZHX-L4.3 緩和版
    - GPT語尾破綻・構文崩壊・意味逸脱を選別
    - 独白（1段落・鉤括弧なし）のみを許容
    - 英数字は8文字以上連続でのみノイズ扱い
    - 半角「...」は全角「…」に正規化してから検証
    """

    if not text or not (20 <= len(text) <= 140):
        print("[NG原因] 長さ不正")
        return False

    # 半角「...」を全角「…」に統一
    text = text.replace("...", "…")
    line = text.strip()

    # 独白：鉤括弧が含まれていないこと
    if "「" in line or "」" in line:
        print("[NG原因] 鉤括弧を含む")
        return False

    # 英数字8文字以上連続はGPTノイズとして排除
    if re.search(r"[a-zA-Z0-9]{8,}", text):
        print("[NG原因] 長い英数字ノイズ")
        return False

    # 異体字・簡体字などの漢字ノイズ
    if re.search(r"[锕鱻靐靇㐀-㛿㐂-㊿㋿㐧䲣]", text):
        print("[NG原因] 異常漢字")
        return False

    # 記号チェック：日本語で通常使わない記号を排除
    if re.search(r"[^\u3040-\u30FF\u4E00-\u9FFF。、！？ー…％：/\-\s]", text):
        print("[NG原因] 不正な記号")
        return False

    # 禁止語チェック
    banned_words = ["構文", "主語", "語尾", "構成"]
    for word in banned_words:
        if word in text:
            print(f"[NG原因] 禁止語を含む: {word}")
            return False

    # 不自然な文末パターン
    unnatural_ending_patterns = [
        r"ではや$", r"だよよ$", r"のかの$", r"でしょうの$", r"なんだがよ$",
        r"だったがよ$", r"らしいけどよ$", r"だったよなぁ$", r"ではか$",
        r"だというのよ$", r"ますことよ$", r"たというわよ$", r"みたいでしたわ$", r"でしてたのよ$"
    ]
    if any(re.search(pat, line) for pat in unnatural_ending_patterns):
        print("[NG原因] 不自然語尾パターン")
        return False

    return True