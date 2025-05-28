# watcher_poemcemetery.py

import json
from datetime import datetime
from tweet_bot import post_to_twitter

DEATH_LOG = "logs/death_log.json"

def latest_death_report():
    with open(DEATH_LOG, "r", encoding="utf-8") as f:
        data = json.load(f)

    entries = [d for d in data if d["type"] == "cemetery"]
    if not entries:
        return None

    latest = sorted(entries, key=lambda x: x["date"], reverse=True)[0]
    return latest

def babaa_react_to_cemetery(death_count):
    phrases = [
        f"{death_count}体、黙ったらしいわよ。",
        f"供養って言うけど、靴下も干してなかったわよ。",
        f"静かだったのよ。いつもの冷蔵庫も泣いてたし。"
    ]
    return {
        "text": phrases[death_count % len(phrases)],
        "tags": ["#供養ババァ", "#構文死者報告"],
        "kz_score": 92,
        "timestamp": datetime.now().isoformat(),
        "style_id": "BA-0010"
    }

if __name__ == "__main__":
    report = latest_death_report()
    if report:
        post = babaa_react_to_cemetery(report["count"])
        post_to_twitter(post)
