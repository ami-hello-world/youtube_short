import openai
import json
import screip 
import os

openai.api_key = os.getenv("OPENAI_API_KEY")



def create_short_script_voicevox(topic_text: str) -> list:
    prompt = f"""
    あなたはYouTubeショート動画の脚本家です。
    以下のネタをもとに台本を作ってください。
    セリフを削ることは許しますが、新たに作る・改変することはできません。
    話者を同じ人にしても構いません。
    ネタの最初にあるタイトルはイッチの発言として扱いまるまる出力してください。
    また最初の発言は絶対に使ってください。
    最初の発言は「イッチ」としてください。
    それ以外の発言者の順番などは自由なのでネタに沿うよう作ってください。


    ▼登場人物（固定3名）
    - くま
        ・ふつう(id:12)、おこ(id:34)、びくびく(id:33)
        icon: "icon.jpeg"
    - イッチ
        ・ノーマル(id:13)、熱血(id:81)、不機嫌(id:82)
        icon: "oji.jpeg"
    - 魔王
        ・ノーマル(id:21)
        icon: "mao.jpeg"

    出力形式は必ず以下のようにJSONリストにしてください：
    [
      {{
        "name": "イッチ",
        "icon": "oji.jpeg",
        "style_id": 13,
        "text": "タイトル"
      }},
      {{
        "name": "イッチ",
        "icon": "oji.jpeg",
        "style_id": 13,
        "text": "セリフ"
      }},
      {{
        "name": "くま",
        "icon": "icon.jpeg",
        "style_id": 13,
        "text": "セリフ"
      }},
      {{
        "name": "魔王",
        "icon": "mao.jpeg",
        "style_id": 13,
        "text": "セリフ"
      }},
    ]

    - 各発言の感情に合わせて style_id を選択してください。
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
    script = json.loads(json_str)

    with open("short_script.txt", "w", encoding="utf-8") as f:
        json.dump(script, f, ensure_ascii=False, indent=2)

    return script


def text_line(text: str) -> list:
   
    prompt = f"""
    あなたは文章を短く分割するアシスタントです。
    以下の文章を自然な場所で10文字前後に区切ってください。
    区切った文章を音声にしてつなげても違和感がないところで区切りなさい。
    違和感がある場合は10文字を超えてもいいのできれいなところで区切りなさい。
    句読点や絵文字などのTTSで読み上げられないものは空白に置き換えてください。
    出力はJSONのリスト形式でお願いします。
    
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


if __name__ == "__main__":
    scraped_data = screip.main()
    #print(scraped_data)
    script =create_short_script_voicevox(scraped_data)
    print(script)
