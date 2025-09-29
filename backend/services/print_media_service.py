from fastapi import UploadFile, HTTPException
from typing import List, Dict, Any
import aiohttp
import asyncio
from datetime import datetime
import uuid
import json
import base64

from backend.models.data_models import (
    PrintMediaDocument,
    AnalysisRequest,
    AnalysisResponse,
    SentimentResult,
    SourceType,
    DocumentType,
    SentimentScore
)
from backend.config.config import get_settings

class PrintMediaService:
    def __init__(self):
        self.settings = get_settings()
        self.pdf_tools_config = self.settings.MCP_SERVERS["pdf_tools"]
        self.doc_edit_config = self.settings.MCP_SERVERS["document_edit"]
        self.pdf_processor_config = self.settings.MCP_SERVERS["pdf_processor"]
        
    async def process_document(self, file: UploadFile) -> PrintMediaDocument:
        """
        Process uploaded document using appropriate MCP server
        """
        try:
            content = await file.read()
            file_extension = file.filename.lower().split('.')[-1]

            if file_extension == 'pdf':
                processed_content, metadata = await self._process_pdf(content, file.filename)
            elif file_extension in ['docx', 'xlsx']:
                processed_content, metadata = await self._process_office_document(content, file_extension, file.filename)
            else:
                # For text files, just decode the content
                processed_content = content.decode('utf-8')
                metadata = {"format": "plain_text"}

            # Get page count for the document
            page_count = await self._get_page_count(content, file_extension)

            # Enhanced metadata
            metadata.update({
                "file_size": len(content),
                "file_type": file_extension,
                "processing_timestamp": datetime.utcnow().isoformat(),
                "page_count": page_count
            })

            return PrintMediaDocument(
                document_type=DocumentType(file_extension),
                content=processed_content,
                file_name=file.filename,
                upload_timestamp=datetime.utcnow(),
                page_count=page_count,
                metadata=metadata
            )

        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error processing document: {str(e)}"
            )

    async def _process_pdf(self, content: bytes, filename: str) -> tuple[str, Dict[str, Any]]:
        """
        Process PDF using combination of MCP servers for comprehensive analysis
        """
        try:
            # Convert content to base64 for API transmission
            content_b64 = base64.b64encode(content).decode('utf-8')
            
            # 1. Use PDF.co MCP Server for initial text extraction and structure analysis
            async with aiohttp.ClientSession() as session:
                pdf_processor_payload = {
                    "file": content_b64,
                    "filename": filename,
                    "options": {
                        "extract_text": True,
                        "extract_metadata": True,
                        "maintain_structure": True,
                        "extract_tables": True
                    }
                }
                
                async with session.post(
                    f"{self.pdf_processor_config['base_url']}/process",
                    json=pdf_processor_payload
                ) as response:
                    if response.status != 200:
                        raise HTTPException(
                            status_code=response.status,
                            detail="PDF processor server error"
                        )
                    pdf_result = await response.json()

            # 2. Use mcp-pdf-tools for additional content analysis
            async with aiohttp.ClientSession() as session:
                pdf_tools_payload = {
                    "file": content_b64,
                    "operations": ["extract_text", "search_content"]
                }
                
                async with session.post(
                    f"{self.pdf_tools_config['base_url']}/analyze",
                    json=pdf_tools_payload
                ) as response:
                    if response.status != 200:
                        raise HTTPException(
                            status_code=response.status,
                            detail="PDF tools server error"
                        )
                    tools_result = await response.json()

            # Combine and structure the results
            processed_content = self._combine_pdf_results(pdf_result, tools_result)
            
            # Enhanced metadata
            metadata = {
                "pdf_version": pdf_result.get("pdf_version"),
                "is_encrypted": pdf_result.get("is_encrypted", False),
                "author": pdf_result.get("metadata", {}).get("author"),
                "creation_date": pdf_result.get("metadata", {}).get("creation_date"),
                "modified_date": pdf_result.get("metadata", {}).get("modified_date"),
                "has_tables": bool(pdf_result.get("tables", [])),
                "table_count": len(pdf_result.get("tables", [])),
                "processing_details": {
                    "processors_used": ["PDF.co MCP", "mcp-pdf-tools"],
                    "text_extraction_confidence": tools_result.get("confidence", 1.0)
                }
            }

            return processed_content, metadata

        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"PDF processing error: {str(e)}"
            )

    async def _process_office_document(self, content: bytes, doc_type: str, filename: str) -> tuple[str, Dict[str, Any]]:
        """
        Process Office documents using document-edit-mcp
        """
        try:
            content_b64 = base64.b64encode(content).decode('utf-8')
            
            async with aiohttp.ClientSession() as session:
                payload = {
                    "file": content_b64,
                    "filename": filename,
                    "type": doc_type,
                    "operations": [
                        "extract_text",
                        "extract_tables",
                        "extract_metadata",
                        "preserve_formatting"
                    ]
                }
                
                async with session.post(
                    f"{self.doc_edit_config['base_url']}/process",
                    json=payload
                ) as response:
                    if response.status != 200:
                        raise HTTPException(
                            status_code=response.status,
                            detail="Document processing server error"
                        )
                    result = await response.json()

            # Structure the content
            processed_content = self._structure_office_content(result)
            
            # Enhanced metadata
            metadata = {
                "document_type": doc_type,
                "author": result.get("metadata", {}).get("author"),
                "last_modified_by": result.get("metadata", {}).get("last_modified_by"),
                "creation_date": result.get("metadata", {}).get("creation_date"),
                "last_modified_date": result.get("metadata", {}).get("last_modified_date"),
                "revision_number": result.get("metadata", {}).get("revision"),
                "has_macros": result.get("metadata", {}).get("has_macros", False),
                "has_tables": bool(result.get("tables", [])),
                "table_count": len(result.get("tables", [])),
                "processing_details": {
                    "processor": "document-edit-mcp",
                    "extraction_confidence": result.get("confidence", 1.0)
                }
            }

            return processed_content, metadata

        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Office document processing error: {str(e)}"
            )

    async def _get_page_count(self, content: bytes, file_extension: str) -> int:
        """
        Get accurate page count of document using appropriate MCP server
        """
        try:
            content_b64 = base64.b64encode(content).decode('utf-8')
            
            if file_extension == 'pdf':
                # Use PDF.co MCP Server for PDF page count
                async with aiohttp.ClientSession() as session:
                    payload = {
                        "file": content_b64,
                        "filename": f"document.{file_extension}",
                        "operation": "get_page_count"
                    }
                    
                    async with session.post(
                        f"{self.pdf_processor_config['base_url']}/info",
                        json=payload
                    ) as response:
                        if response.status != 200:
                            raise HTTPException(
                                status_code=response.status,
                                detail="Error getting PDF page count"
                            )
                        result = await response.json()
                        return result.get("page_count", 1)
            
            elif file_extension in ['docx', 'xlsx']:
                # Use document-edit-mcp for Office documents
                async with aiohttp.ClientSession() as session:
                    payload = {
                        "file": content_b64,
                        "filename": f"document.{file_extension}",
                        "operation": "get_page_count"
                    }
                    
                    async with session.post(
                        f"{self.doc_edit_config['base_url']}/info",
                        json=payload
                    ) as response:
                        if response.status != 200:
                            raise HTTPException(
                                status_code=response.status,
                                detail="Error getting document page count"
                            )
                        result = await response.json()
                        return result.get("page_count", 1)
            
            return 1  # Default for text files

        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error getting page count: {str(e)}"
            )

    def _combine_pdf_results(self, pdf_processor_result: Dict, pdf_tools_result: Dict) -> str:
        """
        Combine and structure results from multiple PDF processors
        """
        combined_content = []

        # Add main content from PDF processor
        if "content" in pdf_processor_result:
            combined_content.append(pdf_processor_result["content"])

        # Add structured content (tables, etc.)
        if "tables" in pdf_processor_result:
            for table in pdf_processor_result["tables"]:
                combined_content.append(f"\nTable Content:\n{table['content']}")

        # Add additional extracted content from PDF tools
        if "extracted_text" in pdf_tools_result:
            combined_content.append(pdf_tools_result["extracted_text"])

        return "\n".join(filter(None, combined_content))

    def _structure_office_content(self, result: Dict) -> str:
        """
        Structure content from Office document processing
        """
        content_parts = []

        # Add main document content
        if "content" in result:
            content_parts.append(result["content"])

        # Add table content if present
        if "tables" in result:
            for table in result["tables"]:
                content_parts.append(f"\nTable Content:\n{table['content']}")

        # Add any headers/footers
        if "headers" in result:
            content_parts.insert(0, "Headers:\n" + "\n".join(result["headers"]))
        if "footers" in result:
            content_parts.append("Footers:\n" + "\n".join(result["footers"]))

        return "\n\n".join(filter(None, content_parts))