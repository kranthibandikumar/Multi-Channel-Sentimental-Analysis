from pydantic import BaseModel, Field, HttpUrl
from typing import List, Dict, Optional, Union
from enum import Enum
from datetime import datetime

class SentimentScore(str, Enum):
    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"

class SourceType(str, Enum):
    SOCIAL_MEDIA = "social_media"
    PRINT_MEDIA = "print_media"
    CALL_RECORDS = "call_records"
    EMAIL = "email"

class SocialMediaPlatform(str, Enum):
    TWITTER = "twitter"
    FACEBOOK = "facebook"
    INSTAGRAM = "instagram"
    LINKEDIN = "linkedin"

class DocumentType(str, Enum):
    PDF = "pdf"
    DOCX = "docx"
    TXT = "txt"
    XLSX = "xlsx"

class PrintMediaDocument(BaseModel):
    document_type: DocumentType
    content: str
    file_name: str
    upload_timestamp: datetime
    page_count: Optional[int] = None
    metadata: Dict = Field(default_factory=dict)

class SocialMediaPost(BaseModel):
    platform: SocialMediaPlatform
    content: str
    post_id: str
    timestamp: datetime
    author: str
    metadata: Dict = Field(default_factory=dict)

class CallRecord(BaseModel):
    call_id: str
    audio_url: Optional[HttpUrl] = None
    transcript: str
    duration: int  # in seconds
    timestamp: datetime
    metadata: Dict = Field(default_factory=dict)

class Email(BaseModel):
    email_id: str
    subject: str
    body: str
    sender: str
    timestamp: datetime
    attachments: List[str] = Field(default_factory=list)
    metadata: Dict = Field(default_factory=dict)

class SentimentResult(BaseModel):
    text: str
    sentiment: SentimentScore
    confidence: float = Field(ge=0.0, le=1.0)
    source_type: SourceType
    timestamp: datetime
    metadata: Dict = Field(default_factory=dict)

class AnalysisRequest(BaseModel):
    source_type: SourceType
    content: Union[SocialMediaPost, PrintMediaDocument, CallRecord, Email]
    additional_context: Optional[Dict] = None

class AnalysisResponse(BaseModel):
    request_id: str
    source_type: SourceType
    sentiment_results: List[SentimentResult]
    analysis_timestamp: datetime
    processing_time: float  # in seconds
    metadata: Dict = Field(default_factory=dict)

class ErrorResponse(BaseModel):
    error_code: str
    message: str
    timestamp: datetime
    details: Optional[Dict] = None