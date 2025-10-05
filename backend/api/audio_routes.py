from fastapi import APIRouter, UploadFile, File, HTTPException
from backend.services.audio_service import AudioAnalyzer
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/audio", tags=["audio"])
audio_analyzer = AudioAnalyzer()

@router.post("/analyze")
async def analyze_audio(file: UploadFile = File(...)):
    """Analyze sentiment in audio file"""
    try:
        if not file.filename.lower().endswith(('.wav', '.mp3', '.m4a', '.ogg')):
            raise HTTPException(status_code=400, detail="Unsupported audio format")
        
        content = await file.read()
        result = await audio_analyzer.analyze_audio(content, file.filename)
        return result
    except Exception as e:
        logger.error(f"Error analyzing audio: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))