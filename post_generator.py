import os
import json
import time
from datetime import datetime
from dotenv import load_dotenv
from openai import OpenAI
import re

# Load environment variables
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
model = os.getenv("OPENAI_MODEL", "gpt-4")

DAILY_LIMIT = 15
DAILY_LIMIT_PATH = "logs/daily_limit.json"
os.makedirs(os.path.dirname(DAILY_LIMIT_PATH), exist_ok=True)

def check_daily_limit():
    today = datetime.now().strftime("%Y-%m-%d")
    if os.path.exists(DAILY_LIMIT_PATH):
        with open(DAILY_LIMIT_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        if data.get(today, 0) >= DAILY_LIMIT:
            print(f"[INFO] 本日分の生成上限（{DAILY_LIMIT}件）に達しました")
            return False
    return True

def increment_daily_count():
    today = datetime.now().strftime("%Y-%m-%d")
    data = {}
    if os.path.exists(DAILY_LIMIT_PATH):
        with open(DAILY_LIMIT_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
    data[today] = data.get(today, 0) + 1
    with open(DAILY_LIMIT_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=True, indent=2)

def generate_babaa_post():
    if not check_daily_limit():
        return None

    max_attempts = 10
    for _ in range(max_attempts):
        try:
            jp_prompt = """
あなたは「70歳の日本人女性になったボブ・ディラン」です。

制度の摩耗、倫理のねじれ、記憶の誤配、感覚の重力異常などを含む独白／会話を生成してください。

【出力形式】次の4パターンのうち**どれか1つ**を選んで生成してください（選択は毎回ランダムで構いません）。  
全体で**140文字以内**に収めてください。

---

① 独白（会話なし・1行・「」なし）  
- 話し手は1人。時間・制度・感覚の混濁を含む自然なモノローグ。  
- リズム・語感に小さな変調を加え、淡く異常な世界観を滲ませてください。  
- 明確な主語・目的語が揃っていなくても構いません。

---

② 会話（2行・発話ごとに「」付き）  
- 2人の発話を1往復。文脈がずれていてもOK。  
- 互いの発言が“なんとなく会話らしい”のに、意味がズレていく構造が理想。  
- 音のリフレインや対話の不均衡を歓迎します。

---

③ 会話（3行・発話3つ・「」付き）  
- 話題が交差し、主語や焦点が移動する。  
- 会話構造のなかに“断裂の予感”や“記憶の不在”を織り込んでください。  
- 発言ごとに少しずつズレが大きくなっていくようにしてください。

---

④ 会話（4行・発話4つ・「」付き）  
- 4人、または1〜2人の発話が再帰・脱線・感覚錯誤を繰り返す構造にしてください。  
- 完全な会話ではなく、**すれ違いの言語列**になることを推奨します。  
- 読解は可能であるが意味が繋がらない“詩的構文崩壊”を目指してください。

---

【語彙制約と表現方法】  
以下の**3カテゴリから合計2つ以上の語彙**を、**そのまま使わず**、「含意・誤読・比喩・象徴」として滲ませてください。

■ 制度語（例：年金、病院、通帳、介護、リモコン、マイナカード、スマホ、ガス代、診察券、ポイント）  
→ 明示せず、「封筒が届いた」「青いカード」「番号で呼ばれた」など間接的な言及にしてください。

■ 哲学語（例：自由、倫理、自己、他者、制度、死、生存、沈黙、責任、国家）  
→ 日常のモノや感情に変換して、「鍵を失くした」「声が聞こえなくなった」「外に出たら戻れない感じがした」など。

■ 抽象語（例：濃度、重さ、距離、隙間、ねじれ、記憶、体温、輪郭、予感）  
→ 五感や感情を通じた表現に変えてください。「味のないみそ汁」「冷たい日差し」「昨日の影が残ってる」など。

---

【構文・音律・ズレの指針】  
- **構文のねじれ**：主語や目的語の欠落、逆順、不自然な接続をあえて使用  
- **音律のズレ**：語感の重複や反復、抑揚の崩壊、テンポの不均衡を用いてください  
- **倫理の転倒**：制度と身体、日常と死、責任と錯覚などの連結を違和感ある形で混ぜてください  
- **時制と認識の混濁**：時間軸が曖昧になる、未来と過去が交錯する、記憶が他人のものになるような言い回しを推奨します  
- **接続詞の削減**：話題を論理で繋がず、**構文的な浮遊**を保ってください  

---

【禁止事項】  
- ストーリー進行（起承転結、説明文）  
- 感動・泣き・明確な主題のある展開  
- 完全な意味破壊（読解不能な文字列）  
- 過度なキャラ付けや過剰な敬語・ギャグ調

---

【出力例（参考のみ）】

・独白：  
通帳のこと思い出したときには、あたしの指先が昔の味になってて、そっちのほうが心配だった。

・2行会話：  
「診察券で番号が呼ばれても、返事できないときあるのよ」  
「うちじゃね、ガスの音で順番が決まるのよ」

・3行会話：  
「スマホの明かりで、倫理が滲むの見えたの」  
「うちのカード、自由だけ削れてたんだけど」  
「体温のことは、昨日もう誰かに渡した気がする」

・4行会話：  
「封筒に戻したら、記憶の重さが増えてたのよ」  
「番号で呼ばれたけど、通路が斜めだったの」  
「マイナの音って、昔より小さくなったと思わない？」  
「それでもあたし、あの沈黙だけ信じてるの」



""".strip()

            response = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": jp_prompt}],
                temperature=1.3,
                timeout=15,
            )
            japanese_text = response.choices[0].message.content.strip()
            print(f"[JP] {japanese_text}")

            dialogue_lines = re.findall(r'「.*?」', japanese_text, re.DOTALL)
            text_len = len(re.sub(r'\s', '', japanese_text))
            is_dialogue = bool(dialogue_lines)

            if is_dialogue:
                if 1 <= len(dialogue_lines) <= 4 and text_len <= 140:
                    increment_daily_count()
                    return {"text": "\n".join(dialogue_lines), "timestamp": datetime.now().isoformat()}
            else:
                if 1 <= text_len <= 140:
                    increment_daily_count()
                    return {"text": japanese_text, "timestamp": datetime.now().isoformat()}

            print(f"[WARN] フォーマット不適合：dialogue={is_dialogue}, lines={len(dialogue_lines)}, text_len={text_len}")
            time.sleep(1)

        except Exception as e:
            print(f"[ERROR] APIエラー: {e}")
            time.sleep(2)

    print("[FAILED] 全試行失敗：投稿スキップ")
    return None
