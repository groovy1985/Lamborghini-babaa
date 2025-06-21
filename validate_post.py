import re

def is_valid_post(text: str) -> bool:
    """
    validate_post.py｜構文国家：KZHX-L4.1 準拠検証器
    - 哲学語・抽象語の直言は一部許容
    - GPT語尾崩壊・異体字混入・会話性の破綻などを検知
    """

    if not text or not (20 <= len(text) <= 140):
        return False

    # 各行を抽出（空白行除去）
    lines = [line.strip() for line in text.strip().splitlines() if line.strip()]
    if len(lines) != 3:
        return False

    # 各行が「」で囲まれていること
    if not all(line.startswith("「") and line.endswith("」") for line in lines):
        return False

    # ❌ ノイズ英数字列（ランダム・非日本語パターン）
    if re.search(r"[a-zA-Z]{4,}", text): return False
    if re.search(r"[0-9]{5,}", text): return False
    if re.search(r"[a-zA-Z0-9]{6,}", text): return False

    # ❌ 中国簡体字・異体字など非日常的な漢字の混入を拒否
    # 例：「锕」「鱻」「靐」など（U+2E80〜U+9FFF 以外のCJK文字）
    if re.search(r"[锕鱻靐靇㐀-㛿㐂-㊿㋿㐧䲣]", text): return False

    # ⚠️ 記号制限：通常の日本語会話で使わない記号を拒否
    if re.search(r"[^\u3040-\u30FF\u4E00-\u9FFF。、！？「」（）ー…％：/\-\s]", text):
        return False

    # ❌ 禁止語（テーマ語・説明語・感動語など）
    banned_words = [
        "構文", "主語", "美しい",
        "物語", "語尾", "構成"
    ]
    if any(word in text for word in banned_words):
        return False

    # ❌ 文末の過剰反復（全行「〜た。」「〜だ。」など）
    if len(re.findall(r"(た|だ|です|ました)[。！？]", text)) == 3:
        return False

    # ❌ CM的短文（文の終止が弱い・短すぎるもの）
    if sum(text.count(p) for p in "。！？") <= 1 and len(text) < 40:
        return False

    # ✅ 応答構造の擬態（会話性の保守）
    reply_hints = ["それで", "やっぱり", "うちも", "たしかに", "でも", "じゃあ", "だから", "のに", "ってこと", "ね", "かも", "よね"]
    if not any(hint in lines[1] for hint in reply_hints) and not any(hint in lines[2] for hint in reply_hints):
        return False

    # ❌ 不自然語尾（GPT誤学習系や崩れた接続）
    unnatural_endings = [
        "ではや", "だよよ", "のかの", "でしょうの", "なんだがよ", 
        "だったがよ", "らしいけどよ", 
        "だったよなぁ", "ではか", 
    ]
    def has_unnatural_ending(line: str) -> bool:
        return any(line.endswith(bad) for bad in unnatural_endings)
    if any(has_unnatural_ending(line) for line in lines):
        return False

    # ❌ 過剰な語彙一致（反復構文の検出）
    def shared_ratio(a, b):
        a_set = set(re.findall(r'[\u3040-\u30FF\u4E00-\u9FFF]+', a))
        b_set = set(re.findall(r'[\u3040-\u30FF\u4E00-\u9FFF]+', b))
        return len(a_set & b_set) / max(len(a_set), 1)
    if shared_ratio(lines[0], lines[2]) > 0.7:
        return False

    return True
