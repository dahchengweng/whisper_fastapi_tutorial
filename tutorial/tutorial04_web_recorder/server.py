"""
Tutorial 04: 網頁直接錄音 + API 串接最小原型
學習目標：
1. 使用 StaticFiles 掛載簡易測試網頁，讓前後端在同一埠號下運行。
2. 接收瀏覽器 MediaRecorder 傳送的 .webm 錄音 Blob 進行辨識。

啟動指令：
uvicorn tutorial.tutorial04_web_recorder.server:app --host 127.0.0.1 --port 8000 --reload
開啟瀏覽器前往：http://127.0.0.1:8000
"""

import os
import shutil
import tempfile
from fastapi import FastAPI, UploadFile, File
from fastapi.staticfiles import StaticFiles
from faster_whisper import WhisperModel
from opencc import OpenCC

app = FastAPI(title="Tutorial 04 - Web Recorder")

MODEL_PATH = r"D:\development\localmodels\faster-whisper-medium"
model = WhisperModel(MODEL_PATH, device="cpu", compute_type="int8", local_files_only=True)
cc = OpenCC('s2twp')

@app.post("/api/transcribe")
async def transcribe(file: UploadFile = File(...)):
    suffix = os.path.splitext(file.filename) or ".webm"
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
        shutil.copyfileobj(file.file, temp_file)
        temp_path = temp_file.name

    try:
        segments, _ = model.transcribe(
            temp_path,
            beam_size=5,
            language="zh",
            initial_prompt="以下是繁體中文的語音內容，請使用台灣繁體中文與標點符號輸出。",
            vad_filter=True
        )
        text = " ".join([cc.convert(seg.text.strip()) for seg in segments])
        return {"text": text}
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)

# 取得目前檔案所在資料夾並掛載靜態 HTML
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
app.mount("/", StaticFiles(directory=CURRENT_DIR, html=True), name="static")
