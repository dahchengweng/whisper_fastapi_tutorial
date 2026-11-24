"""
Tutorial 02: 加入 Silero VAD 靜音過濾與 OpenCC 台灣繁體轉換
學習目標：
1. 使用 vad_filter=True 自動剔除無人聲片段，減少雜訊造成的「幻覺文字」。
2. 結合 initial_prompt 與 OpenCC (s2twp)，確保輸出道地的台灣繁體中文與慣用詞。
"""

import os
from faster_whisper import WhisperModel
from opencc import OpenCC

MODEL_PATH = r"D:\development\localmodels\faster-whisper-medium"
SAMPLE_AUDIO = r"tutorial\sample.wav"

def main():
    if not os.path.exists(SAMPLE_AUDIO):
        print(f"⚠️ 請先放一個測試音檔在：{SAMPLE_AUDIO}")
        return

    # 1. 初始化模型與 OpenCC 轉換器 (s2twp = 簡體轉台灣正體 + 台灣慣用詞彙)
    model = WhisperModel(MODEL_PATH, device="cpu", compute_type="int8", local_files_only=True)
    cc = OpenCC('s2twp')

    # 2. 設定 VAD (語音活動檢測) 參數
    vad_parameters = dict(
        min_silence_duration_ms=500,  # 靜音超過 500 毫秒就進行斷句切割
        threshold=0.5                 # 語音判定門檻 (0.0 ~ 1.0，越高越嚴格)
    )

    print("🎙️ 執行辨識 (已啟用 VAD 過濾與繁體轉換)...")
    segments, info = model.transcribe(
        SAMPLE_AUDIO,
        beam_size=5,
        language="zh",
        initial_prompt="以下是繁體中文的語音內容，請使用台灣繁體中文與標點符號輸出。",
        vad_filter=True,
        vad_parameters=vad_parameters
    )

    print(f"⏱️ 原始音訊長度：{info.duration:.2f} 秒 | VAD 過濾後有效長度：{info.duration_after_vad:.2f} 秒\n")

    for segment in segments:
        raw_text = segment.text.strip()
        tw_text = cc.convert(raw_text)
        print(f"[{segment.start:6.2f}s -> {segment.end:6.2f}s]")
        print(f"  原始輸出：{raw_text}")
        print(f"  繁體轉換：{tw_text}")

if __name__ == "__main__":
    main()
