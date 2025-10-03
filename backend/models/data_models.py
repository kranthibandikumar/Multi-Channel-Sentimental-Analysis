from pydantic import BaseModel, Field
from enum import Enum
from datetime import datetime
from typing import Dict, Any, Optional, List

class DocumentType(str, Enum):
    PDF = "pdf"
    DOCX = "docx"
    XLSX = "xlsx"
    TEXT = "txt"

class SentimentScore(BaseModel):
    positive: float = Field(..., ge=0, le=1)
    negative: float = Field(..., ge=0, le=1)
    neutral: float = Field(..., ge=0, le=1)

class PrintMediaDocument(BaseModel):
    document_type: DocumentType
    content: str
    file_name: str
    upload_timestamp: datetime = Field(default_factory=datetime.now)
    page_count: int = Field(..., gt=0)
    metadata: Dict[str, Any] = Field(default_factory=dict)

class SentimentResult(BaseModel):
    text: str
    score: SentimentScore
    highlights: List[str]

class AnalysisResponse(BaseModel):
    document_id: str
    results: List[SentimentResult]
    metadata: Dict[str, Any]
    timestamp: datetime