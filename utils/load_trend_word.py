import os
import json
import random
from datetime import datetime

def load_trend_word():
    """
    logs/trend_words/2025-06-22.json からトレンド語をランダムで1語返す
    """
    today = datetime.now().strftime("%Y-%m-%d")
    path = f"logs/trend_words/{today}.json"

    if not os.path.exists(path):
        print(f"[WARN] トレンド語ファイルが存在しません: {path}")
        return None

    try:
        with open(path, "r", encoding="utf-8") as f:
            words = json.load(f)
        if not words:
            print("[WARN] トレンド語が空です")
            return None
        return random.choice(words)
    except Exception as e:
        print(f"[ERROR] トレンド語読み込み失敗: {e}")
        return None
