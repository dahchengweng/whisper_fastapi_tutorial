import os
import shutil
import tempfile
import numpy as np
from opencc import OpenCC
from fastapi import UploadFile
from faster_whisper import WhisperModel, decode_audio
from faster_whisper.vad import get_vad_model
from app.models.stt_schema import (
    TranscribeResponse, SegmentItem, VadMetrics, VadScorePoint
)

class WhisperService:
    def __init__(self):
        self.model_path = r"D:\development\localmodels\faster-whisper-medium"
        self.model = WhisperModel(
            self.model_path,
            device="cpu",
            compute_type="int8",
            local_files_only=True
        )
        # 載入內建的 Silero VAD 模型用來計算語音機率能量
        self.vad_model = get_vad_model()
        self.cc = OpenCC('s2twp')

    def _calculate_vad_timeline(self, audio_path: str, sample_rate: int = 16000):
        audio = decode_audio(audio_path, sampling_rate=sample_rate)
        window_size = 512
        
        # 將音訊長度補零 (pad) 至 512 的整數倍，符合 Silero VAD 的輸入限制
        remainder = len(audio) % window_size
        if remainder != 0:
            pad_length = window_size - remainder
            audio = np.pad(audio, (0, pad_length), mode='constant')

        probs = self.vad_model(audio)
        
        timeline = []
        step_sec = window_size / sample_rate
        stride = max(1, int(0.1 / step_sec))
        
        for i in range(0, len(probs), stride):
            timeline.append(VadScorePoint(
                time_sec=round(i * step_sec, 2),
                speech_prob=round(float(probs[i]), 3)
            ))
            
        max_prob = round(float(np.max(probs)), 3) if len(probs) > 0 else 0.0
        avg_prob = round(float(np.mean(probs)), 3) if len(probs) > 0 else 0.0
        return timeline, max_prob, avg_prob
    def transcribe_audio(
        self, 
        file: UploadFile, 
        vad_filter: bool = True, 
        min_silence_duration_ms: int = 500,
        threshold: float = 0.5
    ) -> TranscribeResponse:
        suffix = os.path.splitext(file.filename)[1] or ".webm"
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_audio:
            shutil.copyfileobj(file.file, temp_audio)
            temp_path = temp_audio.name

        try:
            # 1. 計算 VAD 語音機率時間軸
            timeline, max_prob, avg_prob = self._calculate_vad_timeline(temp_path)

            # 2. 執行語音辨識
            vad_params = dict(
                min_silence_duration_ms=min_silence_duration_ms,
                threshold=threshold
            ) if vad_filter else None

            segments, info = self.model.transcribe(
                temp_path,
                beam_size=5,
                language="zh",
                initial_prompt="以下是繁體中文的語音內容，請使用台灣繁體中文與標點符號輸出。",
                vad_filter=vad_filter,
                vad_parameters=vad_params
            )

            result_segments = []
            full_text = []
            for seg in segments:
                tc_text = self.cc.convert(seg.text.strip())
                result_segments.append(SegmentItem(
                    start=round(seg.start, 2),
                    end=round(seg.end, 2),
                    text=tc_text
                ))
                full_text.append(tc_text)

            vad_metrics = VadMetrics(
                enabled=vad_filter,
                threshold=threshold,
                min_silence_duration_ms=min_silence_duration_ms,
                max_speech_prob=max_prob,
                avg_speech_prob=avg_prob,
                timeline=timeline
            )

            return TranscribeResponse(
                status="success",
                language=info.language,
                duration=round(info.duration, 2),
                vad_metrics=vad_metrics,
                full_text=" ".join(full_text),
                segments=result_segments
            )
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)

whisper_service = WhisperService()
