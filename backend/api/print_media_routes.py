from fastapi import APIRouter, UploadFile, File, HTTPException
from backend.services.print_media_service import PrintMediaService
from backend.config.config import get_settings
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/print-media", tags=["print-media"])
print_media_service = PrintMediaService()
settings = get_settings()

@router.post("/analyze")
async def analyze_document(file: UploadFile = File(...)):
    """Upload and analyze sentiment of a document"""
    try:
        # Validate file size
        content = await file.read()
        if len(content) > settings.MAX_DOCUMENT_SIZE:
            raise HTTPException(status_code=413, detail="File too large")
        await file.seek(0)
        
        # Validate file extension
        if not any(file.filename.lower().endswith(ext) for ext in settings.SUPPORTED_FILE_EXTENSIONS):
            raise HTTPException(status_code=400, detail="Unsupported file type")
        
        result = await print_media_service.analyze_document(file)
        return result
    except Exception as e:
        logger.error(f"Error analyzing document: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))