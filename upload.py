from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.auth.transport.requests import Request
import os

# -----------------------------
# 設定
# -----------------------------
SCOPES = ['https://www.googleapis.com/auth/youtube.upload']
TOKEN_FILE = 'token.json'
CLIENT_SECRET_FILE = "client_secret_2_313666857757-882gvch9ums16naq2e9meqjl0angkvcd.apps.googleusercontent.com.json"

# -----------------------------
# 認証取得
# -----------------------------
def get_credentials():
    creds = None
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET_FILE, SCOPES)
            creds = flow.run_local_server(port=8080)  # 初回認証用
        with open(TOKEN_FILE, 'w') as token:
            token.write(creds.to_json())
    return creds

# -----------------------------
# YouTube アップロード
# -----------------------------
def upload_youtube_video(title, description, privacy="public", video_path="final.mp4"):
    creds = get_credentials()
    youtube = build('youtube', 'v3', credentials=creds)
    
    # resumableアップロード対応
    media = MediaFileUpload(video_path, chunksize=10*1024*1024, resumable=True)  # 10MBずつ送信
    request = youtube.videos().insert(
        part="snippet,status",
        body={
            "snippet": {"title": title, "description": description},
            "status": {"privacyStatus": privacy}
        },
        media_body=media
    )

    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            print(f"Uploading {int(status.progress() * 100)}%")
    print("アップロード完了:", response["id"])
    return response

# -----------------------------
# 実行例
# -----------------------------
if __name__ == "__main__":
    res = upload_youtube_video(
        title="テスト動画",
        description="これはテスト用の説明です",
        privacy="private",
        video_path="final.mp4"
    )
