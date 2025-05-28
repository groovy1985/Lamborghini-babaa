import re

def classify_structure(text: str) -> str:
    """
    再構成不能性・音崩壊・揺れ構造などに基づく構文的分類。
    意味ラベリングは行わず、Bot処理不能性／拍の歪みに着目。

    分類結果はZINE整形や統計用（KZ/HX評価とは無関係）。
    """

    # 1. 長句＋終端なし（揺れ放置構文）
    if len(text) > 120 and not text.endswith(("。", "…", ".", "！", "？")):
        return "dangling"

    # 2. 音構造が崩れている（句点なし／読点だけ大量）
    if text.count("、") >= 4 and text.count("。") == 0:
        return "rhythmless"

    # 3. 会話風・引用風の構文（「…」等で始まる）
    if re.match(r"^「.*?」", text) or "孫よ" in text or "誰か" in text:
        return "pseudo-dialogue"

    # 4. 特殊文字・記号過多（視認困難構文）
    if re.search(r"[Ａ-Ｚａ-ｚｦ-ﾟ々〆〤‘’“”＋×÷＝≠∴…]+", text) or re.search(r"[╹¼خ؁♯♭♪’]+", text):
        return "visual-distortion"

    # 5. 改行・空白・途切れ系（拍切断構文）
    if "\n" in text or "  " in text or re.search(r"\s{2,}", text):
        return "broken-flow"

    # 6. 音読拒否構文（母音・子音連打／無発音型）
    if re.search(r"[bcdfghjklmnpqrstvwxyz]{5,}", text.lower()):
        return "unspeakable"

    return "uncategorized"
