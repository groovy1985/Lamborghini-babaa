import random
import json
import os
from datetime import datetime
import openai
import threading
import re
import time
from dotenv import load_dotenv

from utils.validate_post import is_valid_post
from utils.format_utils import trim_text

# 環境変数読み込み
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")
model = os.getenv("OPENAI_MODEL", "gpt-4")

# パス設定
base_dir = os.path.dirname(os.path.abspath(__file__))
style_path = os.path.join(base_dir, "babaa_styles.json")
STYLE_USAGE_PATH = os.path.join(base_dir, "logs/style_usage.json")
DAILY_LIMIT_PATH = os.path.join(base_dir, "logs/daily_limit.json")

# 定数
DAILY_LIMIT = 5
MAX_GLOBAL_ATTEMPTS = 12
lock = threading.Lock()

# スタイル読み込み
with open(style_path, "r", encoding="utf-8") as f:
    styles = json.load(f)

def get_unused_styles():
    used_ids = set()
    if os.path.exists(STYLE_USAGE_PATH):
        try:
            with open(STYLE_USAGE_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, list):
                    used_ids = set(data)
        except Exception as e:
            print(f"⚠️ style_usage.json 読み込みエラー: {e}")
    return [style for style in styles if style["id"] not in use]()
