from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from app.models.stt_schema import TranscribeResponse
from app.services.whisper_service import whisper_service

router = APIRouter(prefix="/api/stt", tags=["Speech-to-Text"])

@router.post("/transcribe", response_model=TranscribeResponse)
async def transcribe(
    file: UploadFile = File(..., description="錄音檔或上傳的音訊檔"),
    vad_filter: bool = Form(True, description="是否啟用 VAD 語音活動檢測"),
    min_silence_duration_ms: int = Form(500, description="判定為靜音的最短毫秒數"),
    threshold: float = Form(0.5, description="語音判定門檻值 (0.0 ~ 1.0)")
):
    if not file.filename:
        raise HTTPException(status_code=400, detail="未收到有效的音訊檔案")
    
    return whisper_service.transcribe_audio(
        file=file,
        vad_filter=vad_filter,
        min_silence_duration_ms=min_silence_duration_ms,
        threshold=threshold
    )
