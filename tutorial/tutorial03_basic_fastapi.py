"""
Tutorial 03: 將 Whisper 包裝成第一個 FastAPI 語音辨識接口
學習目標：
1. 學習在全域載入一次模型，避免每次 HTTP 請求重新讀取耗時。
2. 學習使用 UploadFile 接收音檔，並透過 tempfile 安全建立與刪除暫存檔。
3. 啟動後可開啟 http://127.0.0 使用內建 Swagger UI 測試上傳音檔。

啟動指令：
uvicorn tutorial.tutorial03_basic_fastapi:app --host 127.0.0.1 --port 8000 --reload
"""

import os
import shutil
import tempfile
from fastapi import FastAPI, UploadFile, File, Form
from faster_whisper import WhisperModel
from opencc import OpenCC

app = FastAPI(title="Tutorial 03 - Basic Whisper API")

# 全域單例載入模型與轉換器
MODEL_PATH = r"D:\development\localmodels\faster-whisper-medium"
model = WhisperModel(MODEL_PATH, device="cpu", compute_type="int8", local_files_only=True)
cc = OpenCC('s2twp')

@app.post("/transcribe")
async def transcribe_audio(
    file: UploadFile = File(..., description="上傳音訊檔案"),
    threshold: float = Form(0.5, description="VAD 判定門檻 (0.1 ~ 0.9)")
):
    # 1. 取得副檔名 (注意 os.path.splitext 回傳 tuple，需取索引 1)
    suffix = os.path.splitext(file.filename)[1] or ".wav"

    # 2. 將上傳的串流寫入系統暫存檔
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
        shutil.copyfileobj(file.file, temp_file)
        temp_path = temp_file.name

    try:
        # 3. 呼叫模型進行辨識
        segments, info = model.transcribe(
            temp_path,
            beam_size=5,
            language="zh",
            initial_prompt="以下是繁體中文的語音內容，請使用台灣繁體中文與標點符號輸出。",
            vad_filter=True,
            vad_parameters=dict(threshold=threshold, min_silence_duration_ms=500)
        )

        # 4. 整理回傳結果
        results = []
        for seg in segments:
            results.append({
                "start": round(seg.start, 2),
                "end": round(seg.end, 2),
                "text": cc.convert(seg.text.strip())
            })

        return {
            "filename": file.filename,
            "duration": round(info.duration, 2),
            "threshold_used": threshold,
            "full_text": " ".join([item["text"] for item in results]),
            "segments": results
        }
    finally:
        # 5. 無論成功或報錯，務必清除暫存音檔避免硬碟爆滿
        if os.path.exists(temp_path):
            os.remove(temp_path)
