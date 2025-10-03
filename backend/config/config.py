from pydantic_settings import BaseSettings
from typing import Dict, Any
import os
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    DEBUG: bool = os.getenv('DEBUG', True)
    API_VERSION: str = os.getenv('API_VERSION', '1.0.0')
    
    MCP_SERVERS: Dict[str, Dict[str, Any]] = {
        "pdf_tools": {
            "base_url": os.getenv('MCP_PDF_TOOLS_URL'),
            "api_key": os.getenv('PDF_TOOLS_API_KEY')
        },
        "document_edit": {
            "base_url": os.getenv('MCP_DOCUMENT_EDIT_URL'),
            "api_key": os.getenv('DOCUMENT_EDIT_API_KEY')
        },
        "pdf_processor": {
            "base_url": os.getenv('MCP_PDF_PROCESSOR_URL'),
            "api_key": os.getenv('PDF_PROCESSOR_API_KEY')
        }
    }
    
    MAX_DOCUMENT_SIZE: int = int(os.getenv('MAX_DOCUMENT_SIZE', 10485760))
    SUPPORTED_FILE_EXTENSIONS: list = os.getenv('SUPPORTED_FILE_EXTENSIONS', '.pdf,.docx,.txt,.xlsx').split(',')

    class Config:
        env_file = ".env"

def get_settings() -> Settings:
    return Settings()