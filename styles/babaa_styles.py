# styles/babaa_styles.py

import json
import os
import random

STYLE_FILE = os.path.join(os.path.dirname(__file__), "babaa_styles.json")

def load_styles():
    with open(STYLE_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def get_random_style():
    styles = load_styles()
    unused = [s for s in styles if s.get("status") != "locked"]
    if not unused:
        raise ValueError("❌ 使用可能なスタイルがありません")
    return random.choice(unused)
