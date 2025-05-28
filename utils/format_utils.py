def sanitize_text(text: str) -> str:
    """
    改行・全角スペースなどの整形処理。
    構文国家では拍の崩れが価値になるため、整形は最小限に留める。
    """
    return text.replace("\n", " ").replace("　", " ").strip()


def format_tags(tags: list[str]) -> str:
    """
    タグをスペース区切りに整形し、重複を排除。
    投稿本文とは無関係なので、処理は自由。
    """
    return " ".join(sorted(set(tags)))


def trim_text(text: str, max_length: int = 140) -> str:
    """
    テキストを最大文字数に収めるだけ。
    拍・語尾の崩れを生かすため、末尾に記号などは付けず切るだけとする。
    """
    return text[:max_length]
