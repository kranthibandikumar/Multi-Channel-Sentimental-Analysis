from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from typing import List
from datetime import datetime
import uuid

from backend.models.data_models import (
    PrintMediaDocument,
    AnalysisRequest,
    AnalysisResponse,
    SourceType,
    DocumentType
)
from backend.services.print_media_service import PrintMediaService
from backend.config.config import get_settings

router = APIRouter(prefix="/api/print-media", tags=["Print Media"])
settings = get_settings()