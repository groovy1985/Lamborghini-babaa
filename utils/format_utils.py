import re

def sanitize_text(text: str) -> str:
    """
    改行・全角スペース・制御文字などの最小限の整形を行う。
    構文国家では拍のズレ・句の途切れが価値を持つため、整形は必要最小限。
    """
    text = text.replace("　", " ")        # 全角スペース→半角
    text = text.replace("\n", " ")        # 改行→空白
    text = re.sub(r"\s+", " ", text)      # 連続空白→1つに
    text = text.strip(" 　\n\r\t")        # 両端の制御文字除去
    return text

def format_tags(tags: list[str]) -> str:
    """
    タグをスペース区切りで出力。
    ・重複除去
    ・アルファベット・日本語の混在でも整形対応
    ・ハッシュ記号の自動付与（#なしでも許容）
    """
    cleaned = [tag if tag.startswith("#") else f"#{tag}" for tag in tags]
    return " ".join(sorted(set(cleaned)))

def trim_text(text: str, max_length: int = 140) -> str:
    """
    テキストを最大文字数に収める。
    ・記号や句読点で末尾を整形しない（KZ構文破壊性の確保）
    ・切断による拍の崩壊をそのまま価値として扱う
    """
    if len(text) <= max_length:
        return text
    return text[:max_length].rstrip()
