import re

def is_valid_post(text: str) -> bool:
    """
    validate_post.py｜構文国家：KZHX-L4.2 準拠検証器（ver.1.2整理版）
    - GPT語尾破綻・構文崩壊・意味逸脱の中間ゾーンを精密に選別
    - 会話（3行・鉤括弧あり）または独白（1段落・鉤括弧なし）を許容
    """

    if not text or not (20 <= len(text) <= 140):
        return False

    # 各行抽出
    lines = [line.strip() for line in text.strip().splitlines() if line.strip()]

    if len(lines) == 3:
        # 会話パターン：全行が鉤括弧で囲まれていること
        if not all(
            line.startswith("「") and line.endswith("」") and line.count("「") == 1 and line.count("」") == 1
            for line in lines
        ):
            return False

        # 会話：応答擬態を含むかチェック
        reply_hints = [
            "それで", "やっぱり", "うちも", "たしかに", "でも",
            "じゃあ", "だから", "のに", "ってこと", "ね", "かも", "よね"
        ]
        if not any(hint in line for hint in lines[1:] for hint in reply_hints):
            return False

        # 過剰語彙一致（反復構文検出）
        def shared_ratio(a, b):
            a_set = set(re.findall(r'[\u3040-\u30FF\u4E00-\u9FFF]+', a))
            b_set = set(re.findall(r'[\u3040-\u30FF\u4E00-\u9FFF]+', b))
            return len(a_set & b_set) / max(len(a_set), 1)
        if shared_ratio(lines[0], lines[2]) > 0.7:
            return False

    elif len(lines) == 1:
        # 独白パターン：鉤括弧が含まれていないこと
        if "「" in lines[0] or "」" in lines[0]:
            return False
    else:
        # 1行でも3行でもない場合はNG
        return False

    # 共通チェック：英数字ノイズ
    if re.search(r"[a-zA-Z0-9]{4,}", text):
        return False

    # 異体字・簡体字等
    if re.search(r"[锕鱻靐靇㐀-㛿㐂-㊿㋿㐧䲣]", text):
        return False

    # 記号チェック
    if re.search(r"[^\u3040-\u30FF\u4E00-\u9FFF。、！？「」（）ー…％：/\-\s]", text):
        return False

    # 禁止語
    banned_words = ["構文", "主語", "語尾", "構成"]
    if any(word in text for word in banned_words):
        return False

    # 過剰な文末反復
    if len(re.findall(r"(た|だ|です|ました)[。！？]", text)) == 3:
        return False

    # 不自然語尾検知
    unnatural_ending_patterns = [
        r"ではや$", r"だよよ$", r"のかの$", r"でしょうの$", r"なんだがよ$",
        r"だったがよ$", r"らしいけどよ$", r"だったよなぁ$", r"ではか$",
        r"だというのよ$", r"ますことよ$", r"たというわよ$", r"みたいでしたわ$", r"でしてたのよ$"
    ]
    def has_unnatural_ending(line: str) -> bool:
        return any(re.search(pat, line) for pat in unnatural_ending_patterns)
    if any(has_unnatural_ending(line) for line in lines):
        return False

    return True
