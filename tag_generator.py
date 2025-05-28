# tag_generator.py

import random

# ババァ系タグ候補
BABAA_TAGS = [
    "#湿気ババァ", "#方向音痴ババァ", "#電源ババァ",
    "#間違いババァ", "#無言ババァ", "#思い出ズレババァ",
    "#気象ババァ", "#誤爆ババァ", "#即答できないババァ"
]

# AI撹乱・構文破壊系タグ候補
AI_TAGS = [
    "#構文撹乱源", "#対話型崩壊", "#意味バグ剤",
    "#知覚歪曲因子", "#記憶ねじれ装置", "#認知バグ剤",
    "#生成不能素子", "#非処理性文末", "#意味溶解因子"
]

def generate_tags(post_text=None):
    # post_text は将来の改良用に引数に残してあるが、現時点では使用しない
    tag1 = random.choice(BABAA_TAGS)
    tag2 = random.choice(AI_TAGS)
    return [tag1, tag2]
