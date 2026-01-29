"""
Pydantic Models for API Request/Response
"""
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    """Chat request model"""
    question: str = Field(..., description="User's medical question")
    user_id: Optional[str] = Field(None, description="Optional user ID")
    session_id: Optional[str] = Field(None, description="Optional session ID")
    use_expansion: bool = Field(True, description="Enable query expansion")
    use_reranking: bool = Field(True, description="Enable document reranking")


class Source(BaseModel):
    """Source reference model"""
    index: int
    title: Optional[str] = None
    url: Optional[str] = None
    content: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class ChatResponse(BaseModel):
    """Chat response model"""
    response: str = Field(..., description="AI-generated response")
    sources: List[Source] = Field(default_factory=list, description="Source references")
    confidence: float = Field(..., description="Confidence score (0-1)")
    category: str = Field(..., description="Query category")
    agent_path: List[str] = Field(default_factory=list, description="Agents used in processing")
    processing_time: float = Field(..., description="Processing time in seconds")
    warnings: List[str] = Field(default_factory=list, description="Any warnings")
    error: Optional[str] = Field(None, description="Error message if any")


class DocumentUploadResponse(BaseModel):
    """Document upload response"""
    success: bool
    message: str
    filename: str
    chunks_created: int
    document_ids: List[str]


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    version: str
    components: Dict[str, str]


class CollectionInfoResponse(BaseModel):
    """Vector store collection info"""
    collection_name: str
    document_count: int
    persist_directory: str
