import openai
import os


OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
def select_input():
    theme = themes()
    openai.api_key = OPENAI_API_KEY
    model = "gpt-4o-mini"
    system = (
    f"""
    テーマ：「{theme}」

    以下の条件に従って、2分程度のYouTubeショート用の読み上げ台本を作成してください。

    【ルール】
    - 最初の1行はテーマ名を読み上げること。
    - 以降は1フレーズおよそ15文字前後で区切り、1行ずつ改行すること。
    - 出力は1行ごとにフレーズを配置し、番号や箇条書きは使用しない。
    - AIが創作した名言は絶対に使用しない。
    - 実在する偉人の名言を使うこと。名言のあとは偉人の名前を１行で出力すること。
    - 結構長めの名言をつかってください。
    - 名言には「」などの引用符をつけない。


    """)

    messages = [{"role": "system", "content": system}]    
    response = openai.ChatCompletion.create(
        model=model,
        messages=messages,
        temperature=0.7,
        max_tokens=400  # 名言8個＋区切りを想定した十分な長さ
    )
    
    content = response['choices'][0]['message']['content']
    print(content)
    # 改行ごとにフレーズをリスト化
    phrases = [line.strip() for line in content.split("\n") if line.strip()]
    return phrases

def themes():
    openai.api_key = OPENAI_API_KEY
    model = "gpt-4o-mini"
    system = (
    """
    あなたは台本テーマを考えるアシスタントです。以下の条件に従って新しいテーマを作ってください。

        条件：
        1. 既存テーマリストにあるテーマと参考に新しいテーマを作ってください。
        2. 返答は1つのテーマだけにしてください。
        3. 解説や理由は不要です。
        4. -すらいりません。
        5.～選を使う場合5選までにしてください。

        既存テーマリスト：
        -一生覚えておきたい心を支える言葉4選
        -疲れた心が軽くなる魔法の言葉3選
        -苦しいときに思い出したい言葉
        -一度聞くと忘れられない心に響く名言4選
    """

    )
    messages = [{"role": "system", "content": system}]
    
    response = openai.ChatCompletion.create(
        model=model,
        messages=messages,
        temperature=0.7,
        max_tokens=200
    )
    
    content = response['choices'][0]['message']['content']
    print(f"（テーマ）{content}")
    return content

if __name__ == "__main__":
    select_input()

