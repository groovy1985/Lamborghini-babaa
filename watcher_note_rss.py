# watcher_note_rss.py

import feedparser
from datetime import datetime
from tweet_bot import post_to_twitter

NOTE_RSS = "https://note.com/loveapeace/rss"

def fetch_latest_note():
    feed = feedparser.parse(NOTE_RSS)
    if not feed.entries:
        return None
    entry = feed.entries[0]
    return {
        "title": entry.title,
        "link": entry.link,
        "date": entry.published
    }

def babaa_comment_on_note(title):
    return {
        "text": f"note更新したって？\n『{title}』？ それカビの名前じゃなかった？",
        "tags": ["#更新ババァ", "#錯乱通知"],
        "kz_score": 91,
        "timestamp": datetime.now().isoformat(),
        "style_id": "BA-0021"
    }

if __name__ == "__main__":
    note = fetch_latest_note()
    if note:
        post = babaa_comment_on_note(note["title"])
