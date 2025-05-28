# evaluate_kz.py

import random

# 各評価軸の上限点数（ver.KZ9.2）
MAX_SCORES = {
    "MOD": 25,  # 再現不能性（模倣不能）
    "DCC": 20,  # 意味逸脱性（要約不能）
    "SHK": 15,  # 接続の沈み（構造の不整合）
    "WAV": 20,  # 音・リズムの崩れ
    "RPT": 20   # テンプレ排除・再使用不能性
}

def evaluate_kz(post_text):
    """KZスコア算出（簡易・仮実装）"""
    # 暫定：ランダムに評価軸を揺らしつつ総合スコアを返す
    scores = {
        "MOD": random.randint(20, 25),
        "DCC": random.randint(15, 20),
        "SHK": random.randint(10, 15),
        "WAV": random.randint(15, 20),
        "RPT": random.randint(15, 20)
    }

    total_score = sum(scores.values())

    # スコア記録（オプション：logs/kz_log.json への保存）
    save_kz_score(post_text, scores, total_score)

    return total_score


def save_kz_score(post_text, scores, total_score):
    import os, json
    os.makedirs("logs", exist_ok=True)
    path = "logs/kz_log.json"
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    else:
        data = []

    data.append({
        "text": post_text,
        "scores": scores,
        "total": total_score
    })

    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
