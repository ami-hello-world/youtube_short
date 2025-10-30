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

        既存テーマリスト：
        -節約するための豆知識
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

#野口英雄は⭕️⭕️といった解説
#