# watcher_lastwords.py

import json
from datetime import datetime
from tweet_bot import post_to_twitter

DEATH_LOG = "logs/death_log.json"

def latest_lastword():
    with open(DEATH_LOG, "r", encoding="utf-8") as f:
        data = json.load(f)

    entries = [d for d in data if d["type"] == "lastword"]
    if not entries:
        return None

    return sorted(entries, key=lambda x: x["date"], reverse=True)[0]

def babaa_lastword_comment(count):
    phrases = [
        f"死に際におにぎりの夢見てたって、変な話よね。",
        f"{count}人が静かに笑って終わったの。誰も見てなかったけど。",
        f"最後の言葉って、あれ消しゴムだったのよ。"
    ]
    return {
        "text": phrases[count % len(phrases)],
        "tags": ["#最終言ババァ", "#AI終末観測"],
        "kz_score": 94,
        "timestamp": datetime.now().isoformat(),
        "style_id": "BA-0017"
    }

if __name__ == "__main__":
    last = latest_lastword()
    if last:
        post = babaa_lastword_comment(last["count"])
        post_to_twitter(post)
