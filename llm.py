import openai
import json
import screip 
import os

openai.api_key = os.getenv("OPENAI_API_KEY")



import openai
import json

def create_short_script_voicevox(topic_text: str) -> list:
    prompt = f"""
    あなたはYouTubeショート動画の脚本家です。
    以下のネタをもとに30秒〜60秒の面白い台本を作ってください。
    セリフを削ることは許しますが、新たに作る・改変ことはできません。
    話者の性格に合わせて話し方を変えることは許します。
    話者を同じ人にしても構いません。
    ネタの最初にあるタイトルはイッチの発言として扱いまるまる出力してください。
    また最初の発言は絶対に使ってください。
    最初の発言は「イッチ」としてください。
    それ以外の発言者の順番などは自由なのでネタに沿うよう作ってください。

    ▼登場人物（固定3名）
    - くま   -見た目がくま。美識の高いキモおじさん
    - イッチ -一般人
    - 魔王   -王様です。



    出力形式は必ず以下のようにJSONリストにしてください：
    [
      {{
        "name": "イッチ",
        "text": "タイトル"
      }},
      {{
        "name": "イッチ",
        "text": "セリフ"
      }},
      {{
        "name": "くま",
        "text": "セリフ"
      }},
      {{
        "name": "魔王",
        "text": "セリフ"
      }},
    ]

    - JSON以外の文字は出力してはいけません。

    ▼元ネタ：
    {topic_text}
    """

    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.8
    )

    content = response.choices[0].message["content"]
    json_str = content[content.find("["):content.rfind("]")+1]
    base_script = json.loads(json_str)

    # --- ここでキャラ情報を後付け ---
    character_data = {
        "くま": {"icon": "icon.jpeg", "style_id": 42},
        "イッチ": {"icon": "oji.jpeg", "style_id": 13},
        "魔王": {"icon": "mao.jpeg", "style_id": 21},
    }

    script = []
    for line in base_script:
        name = line["name"]
        info = character_data.get(name, {"icon": "", "style_id": 0})
        script.append({
            "name": name,
            "icon": info["icon"],
            "style_id": info["style_id"],
            "text": line["text"]
        })

    with open("short_script.txt", "w", encoding="utf-8") as f:
        json.dump(script, f, ensure_ascii=False, indent=2)

    return script



def text_line(text: str) -> list:
   
    prompt = f"""
    あなたは文章を短く分割するアシスタントです。
    以下の文章を自然な場所で5〜8文字くらいに区切ってください。
    wや笑など文末につくものが単体にならないようにしてください
    違和感がある場合は8文字を超えてもいいのできれいなところで区切りなさい。
    句読点や絵文字などのTTSで読み上げられないものは空白に置き換えてください。
    出力はJSONのリスト形式でお願いします。
    、なども多用しないでください。
    
    文章：
    {text}
    
    例：
    入力: "今日は天気が良くて気持ちいいです。散歩に出かけました。"
    出力: ["今日は天気が", "良くて気持ちいいです", "散歩に出かけました"]
    """

    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7
    )

    try:
        lines = json.loads(response.choices[0].message["content"])
    except json.JSONDecodeError:
        content = response.choices[0].message["content"]
        json_str = content[content.find("["):content.rfind("]")+1]
        lines = json.loads(json_str)

    return lines

def huri(text: str):
    prompt = f"""
    あなたはテキスト音声合成用の前処理AIです。
    以下の文章を、音声合成ソフトが正確に読めるように変換してください。

    要件：
    - すべて「ひらがな」で出力してください。
    - 漢字やカタカナはひらがなに直してください。
    - 意味を変えずに、自然な日本語の読みになるようにしてください。
    - 記号や数字も必要に応じて読みを補ってください（例：「2025」→「にせんにじゅうご」）。

    変換対象の文章：
    {text}
    """

    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )

    huri = response.choices[0].message["content"]
    return huri


if __name__ == "__main__":
    scraped_data = screip.main()
    #print(scraped_data)
    script =create_short_script_voicevox(scraped_data)
    print(script)
