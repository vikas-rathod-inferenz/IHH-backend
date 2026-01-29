"""
LangGraph State Definition
Defines the state structure for the medical assistant workflow
"""
from typing import TypedDict, List, Dict, Any, Optional, Literal
from langchain_core.documents import Document


class GraphState(TypedDict):
    """
    State of the medical assistant graph
    """
    # Input
    question: str
    user_id: Optional[str]
    session_id: Optional[str]
    
    # Processing flags
    input_validated: bool
    is_medical: bool
    is_emergency: bool
    category: str
    
    # Agent routing
    current_agent: Optional[str]
    requires_rag: bool
    requires_web_search: bool
    requires_human_review: bool
    
    # RAG results
    rag_documents: List[Document]
    rag_response: Optional[str]
    rag_confidence: float
    rag_sources: List[Dict[str, Any]]
    
    # Web search results
    web_search_response: Optional[str]
    web_search_sources: List[Dict[str, Any]]
    web_search_confidence: float
    
    # Image analysis (placeholder for future)
    image_path: Optional[str]
    image_analysis: Optional[Dict[str, Any]]
    
    # Final output
    final_response: str
    final_sources: List[Dict[str, Any]]
    final_confidence: float
    output_validated: bool
    
    # Human-in-the-loop
    human_feedback: Optional[str]
    human_approved: Optional[bool]
    requires_retry: bool
    
    # Metadata
    error: Optional[str]
    warnings: List[str]
    processing_time: float
    agent_path: List[str]
