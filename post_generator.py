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

GOBI_LIST = """
〜しちゃってさ、〜だったと思ってて、〜のはずだったのよね、〜じゃないのよね、〜だったけどさ、〜じゃんか、〜だったりするのよ、〜で止まってたのよ、〜じゃなくてよ、〜しといた方がよかったのに、〜だったような気がするけどね、〜のは初めてだったの、〜って感じしなかった？、〜で終わったのよ、〜するんじゃないのかしら、〜ってことなのかな、〜だと思い込んでたけど、〜じゃないかね、〜かと思ったら違ったのよ、〜だったんかもね、〜っぽかったけど、〜しないとダメなのよ、〜ってことでさ、〜だったのにさあ、〜してたみたいでさ、〜が普通らしいの、〜じゃなくてもいいけどさ、〜で決まりってわけじゃないのよ、〜するにはちょっと早いのよ、〜で済ませたことあるのよ、〜だったじゃないの、〜にしとけばよかったのかもね、〜が多すぎるのよ最近、〜になったらしいじゃん、〜するしかなかったのよ、〜だったのよ結局、〜で片付くのよ、〜のが正しかったのかもね、〜のままだったんだってさ、〜だった頃を思い出すのよ、〜しとくべきだったって、〜でもいいけどさ、〜だったらウケるよね、〜のくせに偉そうだったのよ、〜が足りなかったんじゃないの、〜っぽい雰囲気だったけどね、〜みたいなこと言われたのよ、〜だったかもしれないのよね、〜って結局そういうことでしょ、〜なのがイヤなのよ、〜してくれたってよかったのに、〜だったときはよかったのよ、〜のときは言えなかったのよ、〜のよ昔は、〜じゃなかったらよかったのに、〜で失敗したことあるのよ、〜でも似たようなことあったのよ、〜に似てたのよアレ、〜だったじゃない昔は、〜のときもそうだったのよ、〜してみたけど違ったのよね、〜じゃないにしてもさ、〜で終わりってなんか変だったのよ、〜の時代は違ったのよね、〜だったはずだったのに、〜ってそういうもんじゃないの、〜になると思ってたのに、〜だった気がするのにさ、〜って言ってた人いたのよ、〜で済んでよかったのに、〜のがマシだったかもよ、〜ってのが笑えるのよ、〜で我慢するのが普通なのよ、〜しない方がよかったのかね、〜でも通じた時代だったのよ、〜のに怒られたのよ、〜だったから仕方ないのよ、〜だったらしいわよ、〜に文句言われたくないのよ、〜って言われてたのよ、〜だったら誰でも怒るのよ、〜のときは恥ずかしかったのよ、〜のは気のせいじゃないのよ、〜だったらどうするのよ、〜じゃなくて本当によかったのよ、〜がそうだったのよ、〜にしといてよかったのよ、〜って言いきれないのよ、〜って何の意味があるのかしらね、〜で終わりかと思ったのよ、〜で済んだ話だったのよ、〜するしかなかったのよほんと、〜でも誰も気づかなかったのよ、〜だったけど覚えてないのよ、〜に見えたのよなんとなく、〜のがよかったってことかね、〜だったらウケたけどね、〜で良かったんじゃないのって話、〜にしても変わりなかったのよ、〜のがマシだったんじゃないかって、〜が原因だったのよたぶん、〜で終わったらしいのよ、〜じゃなくてもいいって言われたのよ、〜のこと忘れてたのよ、〜かと思って笑っちゃったのよ、〜だった気がするんだけど、〜みたいなもんだったのよ、〜で通じると思ってたのよ、〜だったときもあるのよ、〜だったら納得するのよ、〜があったって言ってたのよ、〜で驚いたのよまったく
""".strip().split("、")

def ends_with_valid_gobi(line):
    return any(line.endswith(g.strip()) for g in GOBI_LIST)

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
            jp_prompt = f"""
以下の条件で、日本語の構文崩壊型テキストを生成してください。

【バリエーション分岐】
・文数はランダムで2〜4文としてください
・文が2〜4行の場合 → 会話文形式（各文を「」で囲んでください）
・文が1文の場合 → 独白形式（「」なしで、地の文として書いてください）

【語尾仕様】
・語尾は60〜80代の女性が話しそうな自然な口語調としてください。
・以下の語尾リストから選ぶようにしてください（毎文異なるものを使用）：
{ ", ".join(GOBI_LIST) }

【内容】
・生活に関わる何かを話しているようで、具体的な名詞や制度をうまく言えない状態を表現してください
・時事的な現象（行政制度・流行技術など）にも、ズレた形で触れてください
・制度語が出る場合も、誤用・言い間違い・誤解のままにしてください
・文と文は意味を連鎖させず、各発話はバラバラなままで構成してください

【禁止事項】
・愛、希望、記憶、救い、夢、自由などの抽象語は禁止
・登場人物名、明確な時間軸、話としてまとまった内容は禁止
・全体が理解可能な文脈を構成しないでください

【出力形式】
・2〜4文：各文を「」で囲んで会話形式にしてください（句点で閉じてください）
・1文：独白形式で書いてください（「」を使わず、地の文で書いてください）
・全体で140文字以内にしてください
""".strip()

            response = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": jp_prompt}],
                temperature=1.25,
                timeout=15,
            )
            japanese_text = response.choices[0].message.content.strip()
            print(f"[JP] {japanese_text}")

            dialogue_lines = re.findall(r'「.*?」', japanese_text, re.DOTALL)
            text_len = len(re.sub(r'\s', '', japanese_text))

            is_dialogue = bool(dialogue_lines)
            if is_dialogue:
                valid_gobi_count = sum(1 for line in dialogue_lines if ends_with_valid_gobi(line))
                if 1 <= len(dialogue_lines) <= 4 and text_len <= 140 and valid_gobi_count >= len(dialogue_lines):
                    increment_daily_count()
                    return {"text": "\n".join(dialogue_lines), "timestamp": datetime.now().isoformat()}
            else:
                if 1 <= text_len <= 140 and ends_with_valid_gobi(japanese_text):
                    increment_daily_count()
                    return {"text": japanese_text, "timestamp": datetime.now().isoformat()}

            print(f"[WARN] フォーマット不適合：dialogue={is_dialogue}, lines={len(dialogue_lines)}, text_len={text_len}")
            time.sleep(1)

        except Exception as e:
            print(f"[ERROR] APIエラー: {e}")
            time.sleep(2)

    print("[FAILED] 全試行失敗：投稿スキップ")
    return None
