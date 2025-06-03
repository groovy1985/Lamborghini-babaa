# utils/post_logger.py
import os
import json
from datetime import datetime

LOG_PATH = "logs/post_archive.json"

def log_post(text: str, tags: list, kz_score: float):
    os.makedirs("logs", exist_ok=True)
    if os.path.exists(LOG_PATH):
        with open(LOG_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
    else:
        data = []

    data.append({
        "timestamp": datetime.now().isoformat(),
        "text": text,
        "tags": tags,
        "kz_score": kz_score
    })

    with open(LOG_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
