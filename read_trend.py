import os
import json
import requests
from datetime import datetime
from bs4 import BeautifulSoup
import random

# 保存先ディレクトリ
SAVE_DIR = "logs/death_trend_words"
os.makedirs(SAVE_DIR, exist_ok=True)

# 🌐 英語圏トレンドソース
TREND_URL = "https://trends24.in/united-states/"

def get_english_trends(top_n=10):
    """英語圏のトレンドワードをTrends24から取得（BeautifulSoup版）"""
    try:
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
            )
        }
        res = requests.get(TREND_URL, headers=headers, timeout=8)
        res.raise_for_status()
        res.encoding = "utf-8"
        soup = BeautifulSoup(res.text, 'html.parser')

        # トレンドを抽出：ol > li > a でトレンド文字列
        all_trends = [
            tag.text.strip() for tag in soup.select("ol.trend-card__list li a")
        ]

        # 記号多すぎ、長すぎ、短すぎを除外
        filtered = []
        for t in all_trends:
            if not (2 < len(t) <= 40):
                continue
            if not all(c.isalnum() or c.isspace() or c == '-' for c in t):
                continue
            filtered.append(t)

        random.shuffle(filtered)
        return filtered[:top_n]

    except Exception as e:
        print(f"[ERROR] Trends24取得失敗: {e}")
        return []

def get_top_trend_word():
    """吊構文生成用トレンドワード1件を返す"""
    trends = get_english_trends(top_n=10)
    if trends:
        return trends[0]
    return "death"  # fallbackワード

def save_trend_words(words):
    today = datetime.now().strftime("%Y-%m-%d")
    path = os.path.join(SAVE_DIR, f"{today}.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(words, f, ensure_ascii=False, indent=2)
    print(f"[INFO] トレンド語を保存: {path}")

# テスト実行
if __name__ == "__main__":
    try:
        trend_words = get_english_trends()
        print("[INFO] 今日の英語圏トレンド語（Trends24ベース）:")
        for word in trend_words:
            print(f"- {word}")
        save_trend_words(trend_words)
    except Exception as e:
        print(f"[ERROR] {e}")
