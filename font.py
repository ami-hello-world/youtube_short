from PIL import Image, ImageDraw, ImageFont
import textwrap
from pathlib import Path

def create_subtitle_image_with_icon(
    text,
    output_filename="subtitle.png",
    video_size=(1080, 1920),
    font_path="NotoSansJP-Regular.ttf",
    icon_path=None,
    character_name=None,
    font_size=80,
    char_name_font_size=40,
    outline_width=5,
    max_chars_per_line=12,
    text_horizontal_margin=40
):
    width, height = video_size

    # --- アイコンの読み込みとリサイズ ---
    icon = None
    mask = None 
    
    if icon_path:
        try:
            icon_raw = Image.open(icon_path)
            
            icon_rgb = icon_raw.convert("RGB")
            mask = Image.new("L", icon_rgb.size, 0) 
            
            icon_data = icon_rgb.getdata()
            mask_data = []
            
            threshold = 250 
            
            for item in icon_data:
                if item[0] < threshold or item[1] < threshold or item[2] < threshold:
                    mask_data.append(255) # 不透明
                else:
                    mask_data.append(0)   # 透明
                    
            mask.putdata(mask_data)
            
            icon = icon_raw.convert("RGBA")

            icon_diameter = int(font_size * 3.5) 
            icon = icon.resize((icon_diameter, icon_diameter), Image.Resampling.LANCZOS)
            mask = mask.resize((icon_diameter, icon_diameter), Image.Resampling.LANCZOS)
            
        except FileNotFoundError:
            print(f"警告: アイコンファイル '{icon_path}' が見つかりません。アイコンなしで生成します。")
            icon = None
            mask = None
        except Exception as e:
            print(f"警告: アイコンの読み込みまたはリサイズ中にエラーが発生しました: {e}。アイコンなしで生成します。")
            icon = None
            mask = None

    # --- フォントの設定 ---
    try:
        font = ImageFont.truetype(str(Path(font_path)), font_size)
    except Exception as e:
        print(f"エラー: メインフォント '{font_path}' が読み込めません。処理を中断します。")
        return None

    # --- キャラ名用のフォントをロード ---
    char_font = None
    if character_name:
        try:
            char_font = ImageFont.truetype(str(Path(font_path)), char_name_font_size)
        except Exception as e:
            print(f"警告: キャラ名用フォントの読み込みに失敗: {e}。キャラ名は描画されません。")
            character_name = None

    # テキストを折り返す
    lines = textwrap.wrap(text, width=max_chars_per_line)

    # --- 4. 各要素の開始Y座標を計算 (テキスト基準) ---

    # (A) テキストブロックの高さ
    line_spacing = 5
    line_height_draw = font_size + line_spacing
    h_text = (line_height_draw * len(lines)) - line_spacing
    
    # (B) アイコンの高さ
    h_icon = icon.height if icon else 0
    
    # (C) キャラ名の高さ
    h_name = 0
    if character_name and char_font:
        h_name = char_name_font_size
        
    # (D) 各要素間のスペースを定義
    space_name_icon = 15 # キャラ名とアイコンの間のスペース
    space_icon_text = 30 # アイコンとテキストの間のスペース
    space_name_text = 30 # (アイコンがない場合) キャラ名とテキストの間のスペース

    # (E) 各要素の開始Y座標を計算
    
    # [基準] テキストブロックの開始Y座標 (常に中央)
    y_text_block_start = (height - h_text) // 2
    
    # [基準の上] アイコンの開始Y座標
    s_icon_text = space_icon_text if h_icon > 0 else 0
    y_icon_start = y_text_block_start - h_icon - s_icon_text
    
    # [基準のさらに上] キャラ名の開始Y座標
    y_char_name_start = 0 # 初期化
    if h_name > 0:
        if h_icon > 0:
            # アイコンがある場合 -> アイコンの上
            s_name_icon = space_name_icon
            y_char_name_start = y_icon_start - h_name - s_name_icon
        else:
            # アイコンがない場合 -> テキストブロックの上
            s_name_text = space_name_text
            y_char_name_start = y_text_block_start - h_name - s_name_text


    # --- 描画処理 ---
    img = Image.new("RGBA", video_size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    available_width = width - 2 * text_horizontal_margin

    # --- 5. キャラ名の描画 ---
    if character_name and char_font:
        name_bbox = draw.textbbox((0, 0), character_name, font=char_font)
        name_w = name_bbox[2] - name_bbox[0]
        
        centering_offset = max(0, (available_width - name_w) // 2)
        x_name = text_horizontal_margin + centering_offset
        
        y_name = y_char_name_start # 計算済みのY座標
        
        # 黒縁
        for dx in range(-outline_width, outline_width + 1):
            for dy in range(-outline_width, outline_width + 1):
                if dx != 0 or dy != 0:
                    draw.text((x_name + dx, y_name + dy), character_name, font=char_font, fill=(0, 0, 0, 255))
        # 白文字
        draw.text((x_name, y_name), character_name, font=char_font, fill=(255, 255, 255, 255))

    # --- 6. アイコンを配置 ---
    if icon and mask:
        icon_x = (width - icon.width) // 2
        icon_y = y_icon_start # 計算済みのY座標
        
        temp_icon_layer = Image.new("RGBA", video_size, (0, 0, 0, 0))
        
        temp_icon_layer.paste(icon, (icon_x, icon_y), mask) 
        img = Image.alpha_composite(img, temp_icon_layer)
        draw = ImageDraw.Draw(img) # Draw オブジェクトを再生成

    # --- 7. テキストの描画 ---
    y_text = y_text_block_start # 計算済みのY座標 (基準)
    
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

    # 画像を保存
    save_path = Path(output_filename)
    img.save(str(save_path))
    print(f"画像 '{output_filename}' を保存しました。")

    return img


# --- サンプル実行 (4パターン) ---
if __name__ == "__main__":
    test_font_path = "NotoSansJP-Regular.ttf"
    test_icon_path = "icon.jpeg" 

    # --- 1. アイコンあり・キャラ名あり ---
    create_subtitle_image_with_icon(
        "【フル装備】のテストです。キャラ名もアイコンもあります。",
        output_filename="subtitle_full.png",
        font_path=test_font_path,
        icon_path=test_icon_path,
        character_name="テストキャラ名"
    )
    
    print("-" * 20)

    # --- 2. アイコンあり・キャラ名なし ---
    create_subtitle_image_with_icon(
        "【アイコンのみ】のテストです。キャラ名はありません。",
        output_filename="subtitle_icon_only.png",
        font_path=test_font_path,
        icon_path=test_icon_path
        # character_name は省略
    )
    
    print("-" * 20)
    
    # --- 3. アイコンなし・キャラ名あり ---
    create_subtitle_image_with_icon(
        "【キャラ名のみ】のテストです。アイコンはありません。",
        output_filename="subtitle_name_only.png",
        font_path=test_font_path,
        # icon_path は省略
        character_name="テストキャラ名"
    )
    
    print("-" * 20)

    # --- 4. アイコンなし・キャラ名なし ---
    create_subtitle_image_with_icon(
        "【テキストのみ】のテストです。両方ありません。",
        output_filename="subtitle_text_only.png",
        font_path=test_font_path
        # icon_path も character_name も省略
    )