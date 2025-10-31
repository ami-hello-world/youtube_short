import requests
import sounddevice as sd
import numpy as np
from io import BytesIO
import soundfile as sf
from threading import Thread
from pathlib import Path # pathlib をインポート

# サーバー設定
HOST = "127.0.0.1"
PORT = "10101"
SPEAKER = "888753760" # (動作確認済みの「まお」のIDに変更)

# ✅ クエリを生成（同期）
def post_audio_query(text: str) -> dict:
    url = f"http://{HOST}:{PORT}/audio_query"
    params = {"text": text, "speaker": SPEAKER}

    res = requests.post(url, params=params)
    if res.status_code != 200:
        raise Exception(f"音声クエリ生成失敗: {res.status_code}, {res.text}")
    return res.json()


# ✅ 音声合成（同期）
def post_synthesis(query_data: dict) -> bytes:
    url = f"http://{HOST}:{PORT}/synthesis"
    params = {"speaker": SPEAKER}
    headers = {"content-type": "application/json"}

    res = requests.post(url, params=params, headers=headers, json=query_data)
    
    if res.status_code != 200:
        raise Exception(f"音声合成失敗 (ステータスコード): {res.status_code}, {res.text}")
    
    content_type = res.headers.get('Content-Type')
    if content_type != 'audio/wav':
        print(f"--- 警告: 予期しない Content-Type を受信: {content_type} ---")
        print(f"--- APIが返したエラー内容: {res.text} ---")
        raise Exception(f"APIは音声 (audio/wav) ではなく、エラーテキストを返しました: {res.text}")
        
    return res.content


# ✅ 音声再生をスレッドで並列処理
def play_wavfile(wav_data: bytes):
    def play():
        try:
            wav_io = BytesIO(wav_data)
            data, samplerate = sf.read(wav_io)
            sd.play(data, samplerate)
            sd.wait()
        except Exception as e:
            print(f"音声再生でエラーが発生しました: {e}")

    thread = Thread(target=play)
    thread.start()


# ✅ 音声生成＆再生（同期）
def text_to_voice(text: str):
    try:
        query_data = post_audio_query(text)
        wav_data = post_synthesis(query_data)
        #play_wavfile(wav_data)
        
        # --- 修正点: カレントディレクトリに直接保存する ---
        output_path = Path("last_output.wav")
        # -----------------------------------------------
        
        save_wavfile(wav_data, output_path)
        
    except Exception as e:
        print(f"エラー: {e}")
        raise e

# ✅ 音声ファイルを保存する関数
def save_wavfile(wav_data: bytes, filename: str | Path = "output.wav"): # Path型も受け取る
    try:
        filepath = Path(filename)
        
        # --- 修正点: 親ディレクトリがカレント(.)でない場合のみ作成 ---
        if filepath.parent != Path("."):
            filepath.parent.mkdir(parents=True, exist_ok=True)
        # -----------------------------------------------------------
        
        with open(filepath, "wb") as f: # filepath オブジェクトを使用
            f.write(wav_data)
        print(f"音声を保存しました: {filepath}") # filepath オブジェクトを使用
    except Exception as e:
        print(f"音声保存でエラーが発生しました: {e}")



# ✅ テスト実行部分
if __name__ == "__main__":
    while True:
        text = input("テキストを入力してください (qで終了): ")
        if text.lower() == "q":
            break
        try:
            text_to_voice(text)
            print("--- 成功: テストファイル 'last_output.wav' が作成されました ---")
        except Exception as e:
            print(f"--- 失敗: {e} ---")