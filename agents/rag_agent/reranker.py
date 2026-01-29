"""
Reranker Module
Uses Cross-Encoder model to rerank retrieved documents for better relevance
"""
import logging
from typing import List, Tuple
from langchain_core.documents import Document
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
from config import settings

logger = logging.getLogger(__name__)


class DocumentReranker:
    """
    Reranks retrieved documents using HuggingFace Cross-Encoder model
    """
    
    def __init__(self, model_name: str = "cross-encoder/ms-marco-TinyBERT-L-6"):
        """
        Initialize reranker with cross-encoder model
        
        Args:
            model_name: HuggingFace model name for reranking
        """
        self.enabled = True
        self.model_name = model_name
        try:
            self.tokenizer = AutoTokenizer.from_pretrained(
                model_name,
                token=settings.huggingface_token
            )
            self.model = AutoModelForSequenceClassification.from_pretrained(
                model_name,
                token=settings.huggingface_token
            )
            
            # Set model to evaluation mode
            self.model.eval()
            
            # Use GPU if available
            self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
            self.model.to(self.device)
            
            logger.info(f"DocumentReranker initialized with model: {model_name} on {self.device}")
            
        except Exception as e:
            self.enabled = False
            self.device = torch.device("cpu")
            logger.error(f"Error initializing DocumentReranker (disabled): {e}")
    
    def rerank(
        self, 
        query: str, 
        documents: List[Document], 
        top_k: int = None
    ) -> List[Tuple[Document, float]]:
        """
        Rerank documents based on relevance to query
        
        Args:
            query: User query
            documents: List of retrieved documents
            top_k: Number of top documents to return
            
        Returns:
            List of tuples (document, relevance_score) sorted by score
        """
        try:
            if not documents:
                return []
            
            if not self.enabled:
                top_k = top_k or settings.rerank_top_k
                return [(doc, 0.5) for doc in documents[:top_k]]
            
            top_k = top_k or settings.rerank_top_k
            
            # Prepare query-document pairs
            pairs = [[query, doc.page_content] for doc in documents]
            
            # Tokenize and get scores
            with torch.no_grad():
                inputs = self.tokenizer(
                    pairs,
                    padding=True,
                    truncation=True,
                    return_tensors="pt",
                    max_length=512
                ).to(self.device)
                
                outputs = self.model(**inputs)
                scores = outputs.logits.squeeze(-1).cpu().numpy()
            
            # Combine documents with scores
            doc_scores = list(zip(documents, scores))
            
            # Sort by score (descending)
            doc_scores.sort(key=lambda x: x[1], reverse=True)
            
            # Return top_k results
            reranked = doc_scores[:top_k]
            
            logger.info(f"Reranked {len(documents)} documents, returning top {len(reranked)}")
            
            return reranked
            
        except Exception as e:
            logger.error(f"Error reranking documents: {e}")
            # Return original documents with default scores if reranking fails
            return [(doc, 0.5) for doc in documents[:top_k]]
    
    def get_scores(self, query: str, documents: List[Document]) -> List[float]:
        """
        Get relevance scores for documents without reranking
        
        Args:
            query: User query
            documents: List of documents
            
        Returns:
            List of relevance scores
        """
        try:
            if not self.enabled:
                return [0.5] * len(documents)
            pairs = [[query, doc.page_content] for doc in documents]
            
            with torch.no_grad():
                inputs = self.tokenizer(
                    pairs,
                    padding=True,
                    truncation=True,
                    return_tensors="pt",
                    max_length=512
                ).to(self.device)
                
                outputs = self.model(**inputs)
                scores = outputs.logits.squeeze(-1).cpu().numpy().tolist()
            
            return scores
            
        except Exception as e:
            logger.error(f"Error getting scores: {e}")
            return [0.5] * len(documents)


# Global instance
_reranker = None


def get_reranker() -> DocumentReranker:
    """Get or create global reranker instance"""
    global _reranker
    if _reranker is None:
        _reranker = DocumentReranker()
    return _reranker
