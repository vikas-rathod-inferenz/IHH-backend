"""
ChromaDB Vector Store Module
Handles document embedding, storage, and retrieval using ChromaDB
"""
import logging
from typing import List, Dict, Any, Optional
from pathlib import Path
import chromadb
from chromadb.config import Settings as ChromaSettings
from langchain_openai import AzureOpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from config import settings

logger = logging.getLogger(__name__)


class ChromaVectorStore:
    """
    Manages ChromaDB vector store for medical document retrieval
    """
    
    def __init__(self):
        """Initialize ChromaDB vector store with embeddings"""
        try:
            # Initialize Azure OpenAI Embeddings
            self.embeddings = AzureOpenAIEmbeddings(
                azure_endpoint=settings.embedding_azure_endpoint,
                openai_api_key=settings.embedding_api_key,
                openai_api_version=settings.embedding_api_version,
                model=settings.embedding_model_name,
                chunk_size=16
            )
            
            # Initialize ChromaDB client
            self.persist_directory = str(settings.get_chroma_path())
            self.collection_name = settings.chroma_collection_name
            
            # Create ChromaDB vector store
            self.vectorstore = Chroma(
                collection_name=self.collection_name,
                embedding_function=self.embeddings,
                persist_directory=self.persist_directory,
            )
            
            logger.info(f"ChromaDB initialized at {self.persist_directory}")
            
        except Exception as e:
            logger.error(f"Error initializing ChromaDB: {e}")
            raise
    
    def add_documents(self, documents: List[Document]) -> List[str]:
        """
        Add documents to the vector store
        
        Args:
            documents: List of LangChain Document objects
            
        Returns:
            List of document IDs
        """
        try:
            ids = self.vectorstore.add_documents(documents)
            logger.info(f"Added {len(ids)} documents to ChromaDB")
            return ids
        except Exception as e:
            logger.error(f"Error adding documents to ChromaDB: {e}")
            raise
    
    def similarity_search(
        self, 
        query: str, 
        k: int = None,
        filter: Optional[Dict[str, Any]] = None
    ) -> List[Document]:
        """
        Perform similarity search on the vector store
        
        Args:
            query: Search query
            k: Number of results to return (default from settings)
            filter: Optional metadata filter
            
        Returns:
            List of relevant documents
        """
        try:
            k = k or settings.top_k_retrieval
            results = self.vectorstore.similarity_search(
                query=query,
                k=k,
                filter=filter
            )
            logger.info(f"Retrieved {len(results)} documents for query")
            return results
        except Exception as e:
            logger.error(f"Error during similarity search: {e}")
            raise
    
    def similarity_search_with_score(
        self, 
        query: str, 
        k: int = None,
        filter: Optional[Dict[str, Any]] = None
    ) -> List[tuple[Document, float]]:
        """
        Perform similarity search with relevance scores
        
        Args:
            query: Search query
            k: Number of results to return
            filter: Optional metadata filter
            
        Returns:
            List of tuples (document, score)
        """
        try:
            k = k or settings.top_k_retrieval
            results = self.vectorstore.similarity_search_with_score(
                query=query,
                k=k,
                filter=filter
            )
            logger.info(f"Retrieved {len(results)} documents with scores")
            return results
        except Exception as e:
            logger.error(f"Error during similarity search with score: {e}")
            raise
    
    def max_marginal_relevance_search(
        self,
        query: str,
        k: int = None,
        fetch_k: int = 20,
        lambda_mult: float = 0.5,
        filter: Optional[Dict[str, Any]] = None
    ) -> List[Document]:
        """
        Perform MMR search for diverse results
        
        Args:
            query: Search query
            k: Number of results to return
            fetch_k: Number of documents to fetch before MMR
            lambda_mult: Diversity parameter (0=max diversity, 1=max relevance)
            filter: Optional metadata filter
            
        Returns:
            List of diverse relevant documents
        """
        try:
            k = k or settings.top_k_retrieval
            results = self.vectorstore.max_marginal_relevance_search(
                query=query,
                k=k,
                fetch_k=fetch_k,
                lambda_mult=lambda_mult,
                filter=filter
            )
            logger.info(f"MMR search retrieved {len(results)} diverse documents")
            return results
        except Exception as e:
            logger.error(f"Error during MMR search: {e}")
            raise
    
    def delete_collection(self):
        """Delete the entire collection"""
        try:
            self.vectorstore.delete_collection()
            logger.info(f"Deleted collection: {self.collection_name}")
        except Exception as e:
            logger.error(f"Error deleting collection: {e}")
            raise
    
    def get_collection_count(self) -> int:
        """Get number of documents in collection"""
        try:
            count = self.vectorstore._collection.count()
            return count
        except Exception as e:
            logger.error(f"Error getting collection count: {e}")
            return 0
    
    def as_retriever(self, search_type: str = "similarity", search_kwargs: Dict = None):
        """
        Get retriever interface for the vector store
        
        Args:
            search_type: Type of search ("similarity", "mmr", "similarity_score_threshold")
            search_kwargs: Additional search parameters
            
        Returns:
            Retriever object
        """
        search_kwargs = search_kwargs or {"k": settings.top_k_retrieval}
        return self.vectorstore.as_retriever(
            search_type=search_type,
            search_kwargs=search_kwargs
        )


class DocumentProcessor:
    """
    Processes and chunks documents for vector storage
    """
    
    def __init__(self):
        """Initialize document processor with text splitter"""
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=settings.chunk_size,
            chunk_overlap=settings.chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", " ", ""]
        )
        logger.info("DocumentProcessor initialized")
    
    def process_text(
        self, 
        text: str, 
        metadata: Optional[Dict[str, Any]] = None
    ) -> List[Document]:
        """
        Process text into chunks
        
        Args:
            text: Raw text to process
            metadata: Optional metadata to attach to chunks
            
        Returns:
            List of Document chunks
        """
        try:
            chunks = self.text_splitter.split_text(text)
            documents = []
            
            for i, chunk in enumerate(chunks):
                doc_metadata = metadata.copy() if metadata else {}
                doc_metadata["chunk_index"] = i
                doc_metadata["chunk_total"] = len(chunks)
                
                documents.append(Document(
                    page_content=chunk,
                    metadata=doc_metadata
                ))
            
            logger.info(f"Processed text into {len(documents)} chunks")
            return documents
        except Exception as e:
            logger.error(f"Error processing text: {e}")
            raise
    
    def process_documents(self, documents: List[Document]) -> List[Document]:
        """
        Process existing documents into smaller chunks
        
        Args:
            documents: List of Document objects
            
        Returns:
            List of chunked Documents
        """
        try:
            chunked_docs = self.text_splitter.split_documents(documents)
            logger.info(f"Processed {len(documents)} documents into {len(chunked_docs)} chunks")
            return chunked_docs
        except Exception as e:
            logger.error(f"Error processing documents: {e}")
            raise


# Global instances
_vector_store = None
_document_processor = None


def get_vector_store() -> ChromaVectorStore:
    """Get or create global vector store instance"""
    global _vector_store
    if _vector_store is None:
        _vector_store = ChromaVectorStore()
    return _vector_store


def get_document_processor() -> DocumentProcessor:
    """Get or create global document processor instance"""
    global _document_processor
    if _document_processor is None:
        _document_processor = DocumentProcessor()
    return _document_processor
