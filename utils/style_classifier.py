def classify_style(text: str) -> str:
    """
    ババァ投稿のスタイル分類：文体生成には使わず、集計やZINE整形時に使用
    """
    if "夢" in text or "寝た" in text:
        return "dreamy"
    elif "粉" in text or "吸った" in text:
        return "druggy"
    elif "昨日" in text or "時間" in text:
        return "temporal"
    elif "誰か" in text or "名前" in text:
        return "identity"
    else:
        return "unknown"
