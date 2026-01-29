"""
Configuration module for Medical Assistant Backend
Loads environment variables and application settings
"""
import os
from pathlib import Path
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # Application Settings
    app_name: str = "Medical Assistant Backend"
    app_version: str = "1.0.0"
    app_host: str = Field(default="0.0.0.0", alias="APP_HOST")
    app_port: int = Field(default=8000, alias="APP_PORT")
    debug: bool = Field(default=False, alias="DEBUG")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")
    
    # LLM Configuration (Azure OpenAI)
    openai_api_key: str = Field(..., alias="OPENAI_API_KEY")
    openai_api_version: str = Field(default="2024-08-01-preview", alias="OPENAI_API_VERSION")
    azure_endpoint: str = Field(..., alias="AZURE_ENDPOINT")
    model_name: str = Field(default="gpt-4o", alias="MODEL_NAME")
    deployment_name: Optional[str] = Field(default=None, alias="DEPLOYMENT_NAME")
    
    # Embedding Model Configuration
    embedding_api_key: str = Field(..., alias="EMBEDDING_API_KEY")
    embedding_azure_endpoint: str = Field(..., alias="EMBEDDING_AZURE_ENDPOINT")
    embedding_model_name: str = Field(default="text-embedding-ada-002", alias="EMBEDDING_MODEL_NAME")
    embedding_api_version: str = Field(default="2024-08-01-preview", alias="EMBEDDING_API_VERSION")
    
    # Web Search API
    tavily_api_key: str = Field(..., alias="TAVILY_API_KEY")
    
    # Speech API (Eleven Labs) - Optional
    eleven_labs_api_key: Optional[str] = Field(default=None, alias="ELEVEN_LABS_API_KEY")
    
    # Hugging Face Token
    huggingface_token: str = Field(..., alias="HUGGINGFACE_TOKEN")
    
    # LangSmith (Optional)
    langchain_tracing_v2: bool = Field(default=False, alias="LANGCHAIN_TRACING_V2")
    langsmith_api_key: Optional[str] = Field(default=None, alias="LANGSMITH_API_KEY")
    langsmith_endpoint: str = Field(default="https://api.smith.langchain.com", alias="LANGSMITH_ENDPOINT")
    langchain_project: str = Field(default="Medical-Assistant-Backend", alias="LANGCHAIN_PROJECT")
    
    # ChromaDB Settings
    chroma_persist_directory: str = Field(default="./data/chroma_db", alias="CHROMA_PERSIST_DIRECTORY")
    chroma_collection_name: str = Field(default="medical_documents", alias="CHROMA_COLLECTION_NAME")
    
    # File Upload Settings
    max_upload_size: int = Field(default=10485760, alias="MAX_UPLOAD_SIZE")  # 10MB
    allowed_extensions: str = Field(default="pdf,txt,docx,png,jpg,jpeg", alias="ALLOWED_EXTENSIONS")
    upload_directory: str = "./uploads"
    
    # RAG Settings
    chunk_size: int = Field(default=1000, alias="CHUNK_SIZE")
    chunk_overlap: int = Field(default=200, alias="CHUNK_OVERLAP")
    top_k_retrieval: int = Field(default=5, alias="TOP_K_RETRIEVAL")
    rerank_top_k: int = Field(default=3, alias="RERANK_TOP_K")
    confidence_threshold: float = Field(default=0.7, alias="CONFIDENCE_THRESHOLD")
    
    # Temperature settings for LLM
    temperature: float = 0.3
    max_tokens: int = 2000
    
    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "allow"
    
    @property
    def allowed_extensions_list(self) -> list:
        """Return allowed file extensions as a list"""
        return [ext.strip() for ext in self.allowed_extensions.split(",")]
    
    def get_chroma_path(self) -> Path:
        """Get ChromaDB persist directory as Path object"""
        path = Path(self.chroma_persist_directory)
        path.mkdir(parents=True, exist_ok=True)
        return path
    
    def get_upload_path(self) -> Path:
        """Get upload directory as Path object"""
        path = Path(self.upload_directory)
        path.mkdir(parents=True, exist_ok=True)
        return path


# Create global settings instance
settings = Settings()


# Configure LangSmith if enabled
if settings.langchain_tracing_v2 and settings.langsmith_api_key:
    os.environ["LANGCHAIN_TRACING_V2"] = str(settings.langchain_tracing_v2)
    os.environ["LANGSMITH_API_KEY"] = settings.langsmith_api_key
    os.environ["LANGSMITH_ENDPOINT"] = settings.langsmith_endpoint
    os.environ["LANGCHAIN_PROJECT"] = settings.langchain_project
