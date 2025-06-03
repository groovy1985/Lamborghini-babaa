# utils/post_logger.py

import os
import json
from datetime import datetime

# 保存先のパス（logsディレクトリ内）
LOG_PATH = "logs/post_archive.json"

def log_post(text: str, tags: list, kz_score: float):
    """
    投稿内容を構文国家形式で post_archive.json に追加保存する。

    Parameters:
        text (str): 投稿テキスト（改行含む）
        tags (list): タグ2つ（例: ["幻聴", "論理"]）
        kz_score (float): KZスコア（例: 92.5）
    """
    os.makedirs("logs", exist_ok=True)

    # 既存ログの読み込み
    if os.path.exists(LOG_PATH):
        with open(LOG_PATH, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                data = []
    else:
        data = []

    # 新しい投稿を追記
    entry = {
        "timestamp": datetime.now().isoformat(),
        "text": text,
        "tags": tags,
        "kz_score": kz_score
    }
    data.append(entry)

    # 保存
    with open(LOG_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
