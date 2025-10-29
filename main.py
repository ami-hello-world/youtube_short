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
from TTS import text_to_voice
from llm import select_input
from moviepy.video.VideoClip import ImageClip
from haikei import download_random_vertical_video
from font import create_subtitle_image_with_text_margin

def main():
    clips = []
    phrase = select_input()
    fixed_image_path = r"C:\Users\ami\python\subtitle_text_margin_fixed_height_long.png"
    for u in phrase:
        text_to_voice(u)
        audio = AudioFileClip(r"C:\Users\ami\python\last_output.wav")
        voice_len = audio.duration
        create_subtitle_image_with_text_margin(u)
        text_clip = (
            ImageClip(fixed_image_path) 
            .set_duration(voice_len)
        )
        video = text_clip.set_audio(audio)
        clips.append(video)
    final = concatenate_videoclips(clips, method="compose")
    total_duration = final.duration
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
    final_bg = concatenate_videoclips(bg_clips)
    final_bg = final_bg.subclip(0, total_duration)
    result = CompositeVideoClip([final_bg, final])
    result.write_videofile("final.mp4", fps=24)
    print("完了: 'final.mp4' (背景 + 字幕) が作成されました。")


if __name__ == "__main__":
    main()
