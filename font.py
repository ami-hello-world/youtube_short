from PIL import Image, ImageDraw, ImageFont
import textwrap

def create_subtitle_image_with_text_margin(
    text,
    video_size=(1080, 1920),
    font_path="C:/Windows/Fonts/meiryo.ttc",
    font_size=80,
    outline_width=5,
    max_chars_per_line=12,
    text_horizontal_margin=40
):
    width, height = video_size
    font = ImageFont.truetype(font_path, font_size)
    lines = textwrap.wrap(text, width=max_chars_per_line)

    line_spacing = 5
    line_height_draw = font_size + line_spacing 
    rect_height = height // 5

    img = Image.new("RGBA", video_size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    rect_width = width

    rect_y = (height - rect_height) // 2
    draw.rectangle([(0, rect_y), (rect_width, rect_y + rect_height)], fill=(128, 128, 128, 180))

    available_width = rect_width - 2 * text_horizontal_margin
    
    total_text_block_height = (line_height_draw * len(lines)) - line_spacing
    
    y_text = rect_y + (rect_height - total_text_block_height) // 2

    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font)
        text_w = bbox[2] - bbox[0]

        centering_offset = max(0, (available_width - text_w) // 2)
        x_text = text_horizontal_margin + centering_offset

        # 黒縁
        for dx in range(-outline_width, outline_width + 1):
            for dy in range(-outline_width, outline_width + 1):
                if dx != 0 or dy != 0:
                    draw.text((x_text + dx, y_text + dy), line, font=font, fill=(0, 0, 0, 255))
        # 白文字
        draw.text((x_text, y_text), line, font=font, fill=(255, 255, 255, 255))

        y_text += line_height_draw
        
        # --- ★ 修正点 1: ループ内の以下の2行を削除 ---
        # long_text_img = create_subtitle_image_with_text_margin(text)
        # long_text_img.save("subtitle_text_margin_fixed_height_long.png")

    # --- ★ 修正点 2: for ループの外側 (関数が終わる前) に保存処理を追加 ---
    # main.py が読み込む用の固定パス
    save_path = r"C:\Users\ami\python\subtitle_text_margin_fixed_height_long.png"
    # ここまでに描画した「img」を保存する
    img.save(save_path)

    # if __name__ == "__main__": のテスト用に img を返す
    return img


# サンプル使用
if __name__ == "__main__":
    subtitle_img = create_subtitle_image_with_text_margin(
        "これは左右に余白を持たせた字幕です。長い文章でも見切れません。"
    )
    subtitle_img.save("subtitle_text_margin_fixed_height.png")
    
    long_text_img = create_subtitle_image_with_text_margin(
        "これは長文のテストです。"
    )
    # (long.png は関数内で上書き保存されるので、ここの save は不要だが、
    #  動作確認のため残してもOK)
    # long_text_img.save("subtitle_text_margin_fixed_height_long.png")