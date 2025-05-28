def truncate_text(text: str, max_length: int = 140) -> str:
    """140字制限用のトリミング関数"""
    return text if len(text) <= max_length else text[:max_length-1] + "…"

def sanitize_text(text: str) -> str:
    """改行・全角スペースなどの整形"""
    return text.replace("\n", " ").replace("　", " ").strip()

def format_tags(tags: list[str]) -> str:
    """タグをスペース区切りの文字列に整形"""
    return " ".join(sorted(set(tags)))

def trim_text(text: str, max_length: int = 140) -> str:
    """
    テキストを最大文字数に収める（末尾に...つけない）
    """
    return text[:max_length]
