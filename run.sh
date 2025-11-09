#!/bin/bash

# このスクリプトがあるディレクトリに移動
cd /media/ami/HDD/youtube_short

# .envファイルを読み込む
set -a
source /media/ami/HDD/youtube_short/.env
set +a

# venv内のPythonを使ってmain.pyを実行する
# ログファイルも絶対パスで指定する
/media/ami/HDD/youtube_short/youtube/bin/python /media/ami/HDD/youtube_short/main.py >> /media/ami/HDD/youtube_short/task.log 2>&1