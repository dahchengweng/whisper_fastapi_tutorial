"""
Tutorial 05: 計算 Silero VAD 語音機率時間軸並回傳給前端繪圖
學習目標：
1. 呼叫 faster_whisper.vad.get_vad_model() 獨立計算音訊各片段的語音機率 (0.0 ~ 1.0)。
2. 學會使用 np.pad() 將音訊長度補零至 512 的整數倍，解決 Silero VAD 的輸入長度限制。

啟動指令：
uvicorn tutorial.tutorial05_vad_energy_chart.server:app --host 127.0.0.1 --port 8000 --reload
開啟瀏覽器前往：http://127.0.0.1:8000
"""

import os
import shutil
import tempfile
import numpy as np
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.staticfiles import StaticFiles
from faster_whisper import WhisperModel, decode_audio
from faster_whisper.vad import get_vad_model
from opencc import OpenCC

app = FastAPI(title="Tutorial 05 - VAD Energy & Chart")

MODEL_PATH = r"D:\development\localmodels\faster-whisper-medium"
model = WhisperModel(MODEL_PATH, device="cpu", compute_type="int8", local_files_only=True)
vad_model = get_vad_model()
cc = OpenCC('s2twp')

def compute_vad_probs(audio_path: str):
    audio = decode_audio(audio_path, sampling_rate=16000)
    window_size = 512
    # 補零對齊 512 取樣點
    remainder = len(audio) % window_size
    if remainder != 0:
        audio = np.pad(audio, (0, window_size - remainder), mode='constant')

    probs = vad_model(audio)
    # 每 3 個視窗 (約 0.1 秒) 取一個點回傳
    return [round(float(p), 3) for p in probs[::3]]

@app.post("/api/transcribe")
async def transcribe(
    file: UploadFile = File(...),
    threshold: float = Form(0.5)
):
    suffix = os.path.splitext(file.filename) or ".webm"
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
        shutil.copyfileobj(file.file, temp_file)
        temp_path = temp_file.name

    try:
        vad_timeline = compute_vad_probs(temp_path)
        segments, _ = model.transcribe(
            temp_path,
            beam_size=5,
            language="zh",
            initial_prompt="以下是繁體中文的語音內容，請使用台灣繁體中文與標點符號輸出。",
            vad_filter=True,
            vad_parameters=dict(threshold=threshold, min_silence_duration_ms=500)
        )
        text = " ".join([cc.convert(seg.text.strip()) for seg in segments])
        return {
            "text": text,
            "threshold": threshold,
            "vad_timeline": vad_timeline
        }
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
app.mount("/", StaticFiles(directory=CURRENT_DIR, html=True), name="static")
