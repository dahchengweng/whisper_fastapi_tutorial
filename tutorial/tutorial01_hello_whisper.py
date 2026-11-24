"""
Tutorial 01: 載入本地 Faster-Whisper 模型進行基礎語音辨識
學習目標：
1. 學會如何指向本機已下載的模型資料夾 (local_files_only=True)。
2. 了解 model.transcribe() 的基本回傳結構 (segments 與 info)。
"""

import os
from faster_whisper import WhisperModel

# 1. 設定本地模型資料夾路徑 (請確認資料夾內有 model.bin 與 config.json)
MODEL_PATH = r"D:\development\localmodels\faster-whisper-medium"

# 2. 準備一個測試用的音訊檔路徑 (請自行準備一段測試音檔，例如 test.wav 或 test.mp3)
SAMPLE_AUDIO = r"tutorial\sample.wav"

def main():
    if not os.path.exists(MODEL_PATH):
        print(f"❌ 找不到模型路徑：{MODEL_PATH}")
        return

    if not os.path.exists(SAMPLE_AUDIO):
        print(f"⚠️ 請先放一個測試音檔在：{SAMPLE_AUDIO}")
        return

    print("⏳ 正在載入本地 Whisper 模型...")
    # CPU 環境建議使用 device="cpu", compute_type="int8"
    # 若有 NVIDIA GPU 可改為 device="cuda", compute_type="float16"
    model = WhisperModel(
        MODEL_PATH,
        device="cpu",
        compute_type="int8",
        local_files_only=True
    )

    print("🎙️ 開始辨識音訊...")
    # segments 是一個生成器 (Generator)，要透過迴圈讀取才會真正開始推論
    segments, info = model.transcribe(SAMPLE_AUDIO, beam_size=5, language="zh")

    print(f"✅ 偵測語言：{info.language} (信心度：{info.language_probability:.2f})")
    print(f"⏱️ 音訊總長度：{info.duration:.2f} 秒\n")

    for segment in segments:
        print(f"[{segment.start:6.2f}s -> {segment.end:6.2f}s] {segment.text}")

if __name__ == "__main__":
    main()
