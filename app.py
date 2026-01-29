"""
FastAPI Application - Main Entry Point
Medical Assistant Backend with LangGraph Orchestration
"""
import logging
from pathlib import Path
from contextlib import asynccontextmanager
from typing import List

from fastapi import FastAPI, UploadFile, File, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from config import settings
from utils.logger import setup_logging, get_logger
from utils.models import (
    ChatRequest, ChatResponse, DocumentUploadResponse,
    HealthResponse, CollectionInfoResponse, Source
)
from core import get_orchestrator
from agents.rag_agent import get_vector_store, get_document_processor

# Setup logging
setup_logging()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown"""
    # Startup
    logger.info("Starting Medical Assistant Backend...")
    logger.info(f"Environment: {'Development' if settings.debug else 'Production'}")
    
    # Initialize components (lazy loading on first use)
    logger.info("Application started successfully")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Medical Assistant Backend...")


# Create FastAPI app
app = FastAPI(
    title="Medical Assistant Backend",
    description="AI-powered medical chatbot with multi-agent orchestration using LangGraph",
    version=settings.app_version,
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Exception handlers
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "An internal error occurred. Please try again later.",
            "error": str(exc) if settings.debug else None
        }
    )


# Health check endpoint
@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """
    Health check endpoint
    """
    try:
        # Check vector store
        vector_store = get_vector_store()
        doc_count = vector_store.get_collection_count()
        
        return HealthResponse(
            status="healthy",
            version=settings.app_version,
            components={
                "api": "operational",
                "vector_store": "operational",
                "document_count": str(doc_count)
            }
        )
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return HealthResponse(
            status="unhealthy",
            version=settings.app_version,
            components={
                "api": "operational",
                "vector_store": "error",
                "error": str(e)
            }
        )


@app.get("/", tags=["Root"])
async def root():
    """Root endpoint"""
    return {
        "message": "Medical Assistant Backend API",
        "version": settings.app_version,
        "docs": "/docs",
        "health": "/health"
    }


# Chat endpoint
@app.post("/chat", response_model=ChatResponse, tags=["Chat"])
async def chat(request: ChatRequest):
    """
    Process a medical question through the multi-agent system
    
    - **question**: The user's medical question
    - **user_id**: Optional user identifier
    - **session_id**: Optional session identifier
    - **use_expansion**: Enable query expansion (default: true)
    - **use_reranking**: Enable document reranking (default: true)
    """
    try:
        logger.info(f"Processing chat request: {request.question[:100]}...")
        
        # Get orchestrator
        orchestrator = get_orchestrator()
        
        # Process query
        result = orchestrator.process_query(
            question=request.question,
            user_id=request.user_id,
            session_id=request.session_id
        )
        
        # Convert to response model
        response = ChatResponse(
            response=result.get("response", ""),
            sources=[Source(**source) for source in result.get("sources", [])],
            confidence=result.get("confidence", 0.0),
            category=result.get("category", "unknown"),
            agent_path=result.get("agent_path", []),
            processing_time=result.get("processing_time", 0.0),
            warnings=result.get("warnings", []),
            error=result.get("error")
        )
        
        logger.info(f"Chat request completed in {response.processing_time:.2f}s")
        return response
        
    except Exception as e:
        logger.error(f"Error processing chat request: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing request: {str(e)}"
        )


# Document management endpoints
@app.post("/documents/upload", response_model=DocumentUploadResponse, tags=["Documents"])
async def upload_document(file: UploadFile = File(...)):
    """
    Upload a document to the knowledge base
    
    Supported formats: PDF, TXT, DOCX
    """
    try:
        logger.info(f"Uploading document: {file.filename}")
        
        # Validate file extension
        file_ext = Path(file.filename).suffix.lower()
        if file_ext.replace(".", "") not in settings.allowed_extensions_list:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File type not allowed. Supported: {settings.allowed_extensions}"
            )
        
        # Save file
        upload_path = settings.get_upload_path()
        file_path = upload_path / file.filename
        
        with open(file_path, "wb") as f:
            content = await file.read()
            
            # Check file size
            if len(content) > settings.max_upload_size:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"File too large. Maximum size: {settings.max_upload_size} bytes"
                )
            
            f.write(content)
        
        # Process document
        # Read text from file (simplified - in production use proper parsers)
        if file_ext == ".txt":
            with open(file_path, "r", encoding="utf-8") as f:
                text = f.read()
        else:
            # For PDF/DOCX, you'd use docling or similar
            text = f"Document content from {file.filename}"
        
        # Process and add to vector store
        doc_processor = get_document_processor()
        chunks = doc_processor.process_text(
            text=text,
            metadata={
                "source": file.filename,
                "file_type": file_ext,
                "upload_path": str(file_path)
            }
        )
        
        vector_store = get_vector_store()
        doc_ids = vector_store.add_documents(chunks)
        
        logger.info(f"Document processed: {file.filename}, {len(chunks)} chunks created")
        
        return DocumentUploadResponse(
            success=True,
            message="Document uploaded and processed successfully",
            filename=file.filename,
            chunks_created=len(chunks),
            document_ids=doc_ids
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading document: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing document: {str(e)}"
        )


@app.get("/documents/collection-info", response_model=CollectionInfoResponse, tags=["Documents"])
async def get_collection_info():
    """
    Get information about the document collection
    """
    try:
        vector_store = get_vector_store()
        doc_count = vector_store.get_collection_count()
        
        return CollectionInfoResponse(
            collection_name=settings.chroma_collection_name,
            document_count=doc_count,
            persist_directory=settings.chroma_persist_directory
        )
        
    except Exception as e:
        logger.error(f"Error getting collection info: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving collection info: {str(e)}"
        )


@app.delete("/documents/collection", tags=["Documents"])
async def delete_collection():
    """
    Delete the entire document collection (use with caution!)
    """
    try:
        vector_store = get_vector_store()
        vector_store.delete_collection()
        
        logger.warning("Document collection deleted")
        
        return {"success": True, "message": "Collection deleted successfully"}
        
    except Exception as e:
        logger.error(f"Error deleting collection: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting collection: {str(e)}"
        )


# Run the application
if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app:app",
        host=settings.app_host,
        port=settings.app_port,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    )
