# TextClip は video.tools.credits から
from moviepy.video.tools.credits import TextClip
import PIL.Image
if not hasattr(PIL.Image, 'ANTIALIAS'):
    PIL.Image.ANTIALIAS = PIL.Image.LANCZOS
from moviepy.video.compositing.CompositeVideoClip import CompositeVideoClip
from moviepy.video.io.VideoFileClip import VideoFileClip
from moviepy.audio.io.AudioFileClip import AudioFileClip
from moviepy.video.compositing.concatenate import concatenate_videoclips
from moviepy.video.fx.all import resize
from TTS import text_to_voicevox
from llm import create_short_script_voicevox, text_line,huri
from moviepy.video.VideoClip import ImageClip
from haikei import download_random_vertical_video
from font import create_subtitle_image_with_icon
from pathlib import Path
from screip import main as sc
import time
from moviepy.editor import concatenate_audioclips
from upload import upload_youtube_video
from moviepy.audio.AudioClip import CompositeAudioClip
from moviepy.audio.fx.all import audio_loop
from moviepy.audio.io.AudioFileClip import AudioFileClip
import datetime

def main():
    title, conversation_data  = sc()
    motoneta = [title] + conversation_data
    fixed_image_path = Path("subtitle.png")
    daihon = create_short_script_voicevox(motoneta)
    
    subtitle_clips = []
    audio_clips = []
    start_time = 0.0

    for idx, i in enumerate(daihon):
        icon_path = i["icon"]
        character_name = i["name"]
        style_id = int(i["style_id"])
        phrases = text_line(i["text"])
        
        # 長文ごとの音声生成
        long_text = "".join(phrases)
        audio_path = f"temp_audio_{idx}.wav"
        h= huri(long_text)
        text_to_voicevox(h, style_id, audio_path)
        audio = AudioFileClip(audio_path)
        audio_clips.append(audio)
        
        # 長文内で字幕を文字数割合で割り振る
        total_chars = sum(len(p) for p in phrases)
        local_start = start_time
        for p in phrases:
            duration = len(p) / total_chars * audio.duration
            create_subtitle_image_with_icon(text=p,icon_path= icon_path, character_name=character_name)
            clip = ImageClip(str(fixed_image_path)).set_duration(duration).set_start(local_start)
            subtitle_clips.append(clip)
            local_start += duration
        
        start_time += audio.duration

    # 音声を連結
    full_audio = concatenate_audioclips(audio_clips)

    # 背景動画の準備
    total_duration = start_time
    print(f"字幕動画の総再生時間: {total_duration:.2f} 秒")
    bg_clips = []
    total_bg_duration = 0
    bg_counter = 0
    while total_bg_duration < total_duration:
        print(f"背景動画の長さ: {total_bg_duration:.2f} / {total_duration:.2f} 秒 ...")
        bg_filename = f"background_{bg_counter}.mp4"
        download_random_vertical_video(filename=bg_filename)
        clip = VideoFileClip(bg_filename).fx(resize, newsize=(1080, 1920))
        bg_clips.append(clip)
        total_bg_duration += clip.duration
        bg_counter += 1

    print(f"背景動画を {bg_counter} 本集めました (合計: {total_bg_duration:.2f} 秒)")
    final_bg = concatenate_videoclips(bg_clips).subclip(0, total_duration)

    # 最終合成
    final = CompositeVideoClip([final_bg, *subtitle_clips])
    music = AudioFileClip("ハラハラするメロディー_takusin.wav").subclip(13.0)
    music = audio_loop(music, duration=final.duration)
    music = music.volumex(0.3)
    final_audio = CompositeAudioClip([full_audio, music])
    final = final.set_audio(final_audio)
    bom = AudioFileClip("bom.mp3")
    final_audio = concatenate_audioclips([final_audio, bom])
    final = final.set_audio(final_audio)

    try:
        final.write_videofile("final.mp4", fps=24)
        print("完了: 'final.mp4' (背景 + 字幕) が作成されました。")
        
        # 生成成功時にYouTubeへアップロード
        
        upload_youtube_video(
            title=title,  # ネタの冒頭30文字をタイトルに
            description="VOICEVOX:麒ヶ島宗麟,白上虎太郎,四国めたん,玄野武宏,ずんだもん,青山龍星,春日部つむぎ,波音リツ,剣崎雌雄,代屋モント にじボイス #2ch面白いスレ #2chまとめ #2ch #くまさん #くま #くまさんショート #くまショート",
            privacy="public",
            video_path="final.mp4"
        )
        
        print("✅ YouTubeへのアップロードを開始しました。")
        dt_now = datetime.datetime.now()
        print(dt_now)
    except Exception as e:
        print(f"❌ 動画生成中にエラーが発生しました: {e}")
        dt_now = datetime.datetime.now()
        print(dt_now)
        
if __name__ == "__main__":
    main()
