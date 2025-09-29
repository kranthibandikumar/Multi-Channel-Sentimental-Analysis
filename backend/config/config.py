from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import Dict, List

class Settings(BaseSettings):
    # API Settings
    API_VERSION: str = "1.0.0"
    PROJECT_NAME: str = "Multi-Channel Sentiment Analysis"
    DEBUG: bool = True

    # MCP Server Configurations
    MCP_SERVERS: Dict[str, Dict] = {
        "pdf_tools": {
            "name": "mcp-pdf-tools",
            "base_url": "",  # Will be configured later
            "features": ["merge_pdfs", "extract_pages", "search_content"]
        },
        "document_edit": {
            "name": "document-edit-mcp",
            "base_url": "",  # Will be configured later
            "features": ["create_pdf", "convert_word_to_pdf", "edit_word_excel"]
        },
        "pdf_processor": {
            "name": "PDF.co MCP Server",
            "base_url": "",  # Will be configured later
            "features": ["parsing", "conversion", "data_extraction"]
        }
    }

    # Channel Settings
    SUPPORTED_CHANNELS: List[str] = [
        "social_media",
        "print_media",
        "call_records",
        "emails"
    ]

    # Social Media Settings
    SOCIAL_MEDIA_PLATFORMS: List[str] = [
        "twitter",
        "facebook",
        "instagram",
        "linkedin"
    ]

    # Print Media Settings
    SUPPORTED_DOCUMENT_TYPES: List[str] = [
        "pdf",
        "docx",
        "txt",
        "xlsx"
    ]

    # Model Settings
    SENTIMENT_MODEL_NAME: str = "distilbert-base-uncased-finetuned-sst-2-english"
    
    class Config:
        case_sensitive = True
        env_file = ".env"

@lru_cache()
def get_settings() -> Settings:
    """
    Get cached settings instance.
    Returns:
        Settings: Application settings
    """
    return Settings()

# Create a global settings instance
settings = get_settings()