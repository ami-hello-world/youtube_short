import requests
import sounddevice as sd
import numpy as np
from io import BytesIO
import soundfile as sf
from threading import Thread
from pathlib import Path

# -----------------------------
# VOICEVOXサーバー設定
# -----------------------------
HOST = "127.0.0.1"
PORT = "50021"


# ✅ 音声クエリ生成（速度調整付き）
def post_audio_query(text: str, speaker_id: int, speed: float = 1.2):
    """
    speed: 1.0が標準、1.2なら少し早く、0.8なら遅く
    """
    url = f"http://{HOST}:{PORT}/audio_query"
    params = {"text": text, "speaker": speaker_id}

    res = requests.post(url, params=params)
    if res.status_code != 200:
        raise Exception(f"音声クエリ生成失敗: {res.status_code}, {res.text}")

    query_data = res.json()
    query_data["speedScale"] = speed  # ここで速度を調整
    return query_data



# ✅ 音声合成
def post_synthesis(query_data: dict, speaker_id: int):
    url = f"http://{HOST}:{PORT}/synthesis"
    params = {"speaker": speaker_id}
    headers = {"content-type": "application/json"}

    res = requests.post(url, params=params, headers=headers, json=query_data)

    if res.status_code != 200:
        raise Exception(f"音声合成失敗: {res.status_code}, {res.text}")

    if res.headers.get("Content-Type") != "audio/wav":
        print(f"--- 警告: 予期しない Content-Type: {res.headers.get('Content-Type')} ---")
        raise Exception(f"APIがエラーを返しました: {res.text}")

    return res.content


# ✅ 音声保存
def save_wavfile(wav_data: bytes, filename: str | Path = "output.wav"):
    try:
        filepath = Path(filename)
        if filepath.parent != Path("."):
            filepath.parent.mkdir(parents=True, exist_ok=True)
        with open(filepath, "wb") as f:
            f.write(wav_data)
        print(f"音声を保存しました: {filepath}")
    except Exception as e:
        print(f"音声保存でエラーが発生しました: {e}")


# ✅ 音声再生
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


# ✅ テキスト→音声ファイル化（VOICEVOX対応）
def text_to_voicevox(text: str, style_id: int, output_path: str | Path = "output.wav", play=False):
    """
    text: セリフ文字列
    style_id: VOICEVOXのスタイルID（例: 12, 34, 81など）
    output_path: 出力先パス
    play: Trueなら再生
    """
    query_data = post_audio_query(text, style_id)
    wav_data = post_synthesis(query_data, style_id)
    save_wavfile(wav_data, output_path)


# ✅ テスト実行
if __name__ == "__main__":
    # 例: 白上虎太郎(ふつう=12)
    text = "テスト用でえええす。"
    style_id = "12"
    text_to_voicevox(text, style_id, "last_output.wav", play=True)
    print("--- 成功: 'last_output.wav' に保存されました ---")
