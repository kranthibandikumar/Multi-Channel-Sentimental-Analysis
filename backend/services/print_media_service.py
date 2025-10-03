from io import BytesIO
import PyPDF2
from fastapi import UploadFile, HTTPException
from typing import List, Dict, Any
from datetime import datetime
import uuid
import logging
from backend.models.data_models import PrintMediaDocument, AnalysisResponse, SentimentResult
from backend.config.config import get_settings
from backend.services.sentiment_analyzer import SentimentAnalyzer

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)  # Add this line for detailed logging

class PrintMediaService:
    def __init__(self):
        try:
            self.settings = get_settings()
            self.sentiment_analyzer = SentimentAnalyzer()
            logger.debug("PrintMediaService initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing PrintMediaService: {str(e)}")
            raise

    async def analyze_document(self, file: UploadFile) -> AnalysisResponse:
        """Process and analyze document sentiment"""
        try:
            logger.debug(f"Starting analysis for file: {file.filename}")
            
            content = await file.read()
            logger.debug(f"File read successfully, size: {len(content)} bytes")
            
            text_content = await self._extract_text(content, file.filename)
            logger.debug(f"Text extracted, length: {len(text_content)} characters")
            
            if not text_content:
                raise ValueError("No text content extracted from document")
            
            analysis_result = self.sentiment_analyzer.analyze_text(
                text=text_content,
                timestamp=datetime.now()
            )
            logger.debug("Sentiment analysis completed")
            
            result = SentimentResult(
                text=text_content[:1000] + "..." if len(text_content) > 1000 else text_content,
                score=analysis_result["sentiment"],
                highlights=[j[0] for j in analysis_result.get("justification", [])]
            )
            
            return AnalysisResponse(
                document_id=str(uuid.uuid4()),
                results=[result],
                metadata={"filename": file.filename},
                timestamp=datetime.now()
            )
        except Exception as e:
            logger.error(f"Error in analyze_document: {str(e)}", exc_info=True)
            raise HTTPException(status_code=500, detail=f"Analysis error: {str(e)}")

    async def _extract_text(self, content: bytes, filename: str) -> str:
        try:
            logger.debug(f"Extracting text from {filename}")
            pdf_reader = PyPDF2.PdfReader(BytesIO(content))
            text_content = ""
            
            for page in pdf_reader.pages:
                text_content += page.extract_text() + "\n"
            
            if not text_content:
                raise ValueError("No text extracted from PDF")
                
            return text_content.strip()
        except Exception as e:
            logger.error(f"Error extracting text: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=500, 
                detail=f"Error extracting text from PDF: {str(e)}"
            )
        
    async def process_document(self, file: UploadFile) -> PrintMediaDocument:
        """Process uploaded document"""
        try:
            content = await file.read()
            text_content = await self._extract_text(content, file.filename)
            
            return PrintMediaDocument(
                document_type=DocumentType.PDF,
                content=text_content,
                file_name=file.filename,
                page_count=1,  # Simple default
                metadata={"timestamp": datetime.now()}
            )
        except Exception as e:
            logger.error(f"Error processing document: {str(e)}", exc_info=True)
            raise HTTPException(status_code=500, detail=f"Processing error: {str(e)}")