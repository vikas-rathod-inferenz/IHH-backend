"""
RAG Agent Module
Main RAG agent with advanced retrieval, query expansion, and reranking
"""
import logging
from typing import List, Dict, Any, Optional, Tuple
from langchain_core.documents import Document
from langchain_openai import AzureChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from config import settings
from agents.rag_agent.vector_store import get_vector_store
from agents.rag_agent.query_expander import get_query_expander
from agents.rag_agent.reranker import get_reranker

logger = logging.getLogger(__name__)


class RAGAgent:
    """
    Advanced RAG Agent with query expansion, reranking, and confidence scoring
    """
    
    def __init__(self):
        """Initialize RAG Agent with all components"""
        try:
            # Initialize LLM
            self.llm = AzureChatOpenAI(
                azure_endpoint=settings.azure_endpoint,
                openai_api_key=settings.openai_api_key,
                openai_api_version=settings.openai_api_version,
                deployment_name=settings.deployment_name or settings.model_name,
                temperature=settings.temperature,
                # max_tokens=settings.max_tokens
            )
            
            # Initialize components
            self.vector_store = get_vector_store()
            self.query_expander = get_query_expander()
            self.reranker = get_reranker()
            
            # Create response generation prompt
            self.response_prompt = ChatPromptTemplate.from_messages([
                ("system", """You are a highly knowledgeable medical assistant. Use the provided context to answer the user's question accurately and professionally.

Guidelines:
1. Base your answer primarily on the provided context
2. If the context doesn't contain sufficient information, acknowledge this
3. Provide medical information in clear, accessible language
4. Include relevant medical terminology with explanations
5. Always recommend consulting healthcare professionals for diagnosis and treatment
6. Never provide emergency medical advice - direct users to seek immediate care if needed

Context:
{context}

Source References:
{sources}"""),
                ("human", "{question}")
            ])
            
            logger.info("RAGAgent initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing RAGAgent: {e}")
            raise
    
    def retrieve_documents(
        self, 
        query: str, 
        use_expansion: bool = True,
        use_reranking: bool = True,
        top_k: int = None
    ) -> Tuple[List[Document], List[float]]:
        """
        Retrieve relevant documents using advanced retrieval pipeline
        
        Args:
            query: User query
            use_expansion: Whether to use query expansion
            use_reranking: Whether to use document reranking
            top_k: Number of documents to return
            
        Returns:
            Tuple of (documents, relevance_scores)
        """
        try:
            # Step 1: Query expansion
            search_query = query
            if use_expansion:
                expanded_query = self.query_expander.create_expanded_query(query)
                search_query = expanded_query
                logger.info(f"Expanded query: {search_query}")
            
            # Step 2: Initial retrieval from vector store
            k_retrieval = (top_k or settings.rerank_top_k) * 3 if use_reranking else (top_k or settings.top_k_retrieval)
            
            retrieved_docs = self.vector_store.similarity_search(
                query=search_query,
                k=k_retrieval
            )
            
            if not retrieved_docs:
                logger.warning("No documents retrieved from vector store")
                return [], []
            
            logger.info(f"Retrieved {len(retrieved_docs)} documents from vector store")
            
            # Step 3: Reranking
            if use_reranking and len(retrieved_docs) > 0:
                reranked_results = self.reranker.rerank(
                    query=query,
                    documents=retrieved_docs,
                    top_k=top_k or settings.rerank_top_k
                )
                documents = [doc for doc, score in reranked_results]
                scores = [float(score) for doc, score in reranked_results]
                logger.info(f"Reranked to top {len(documents)} documents")
            else:
                documents = retrieved_docs[:top_k or settings.top_k_retrieval]
                scores = [1.0] * len(documents)
            
            return documents, scores
            
        except Exception as e:
            logger.error(f"Error retrieving documents: {e}")
            return [], []
    
    def calculate_confidence(self, documents: List[Document], scores: List[float]) -> float:
        """
        Calculate confidence score based on retrieval quality
        
        Args:
            documents: Retrieved documents
            scores: Relevance scores
            
        Returns:
            Confidence score between 0 and 1
        """
        try:
            if not documents or not scores:
                return 0.0
            
            # Average of top scores
            avg_score = sum(scores) / len(scores)
            
            # Normalize to 0-1 range (assuming scores are roughly -10 to 10)
            normalized_score = max(0.0, min(1.0, (avg_score + 10) / 20))
            
            # Penalty for having very few documents
            doc_count_factor = min(1.0, len(documents) / settings.rerank_top_k)
            
            confidence = normalized_score * (0.7 + 0.3 * doc_count_factor)
            
            logger.info(f"Calculated confidence: {confidence:.3f}")
            return confidence
            
        except Exception as e:
            logger.error(f"Error calculating confidence: {e}")
            return 0.5
    
    def generate_response(
        self, 
        query: str, 
        documents: List[Document],
        include_sources: bool = True
    ) -> Dict[str, Any]:
        """
        Generate response using retrieved documents
        
        Args:
            query: User query
            documents: Retrieved documents
            include_sources: Whether to include source references
            
        Returns:
            Dictionary with response, sources, and metadata
        """
        try:
            if not documents:
                return {
                    "response": "I don't have enough information in my knowledge base to answer this question accurately. Please try rephrasing your question or consult a healthcare professional.",
                    "sources": [],
                    "confidence": 0.0
                }
            
            # Prepare context from documents
            context = "\n\n".join([
                f"[Document {i+1}]\n{doc.page_content}"
                for i, doc in enumerate(documents)
            ])
            
            # Prepare source references
            sources = []
            if include_sources:
                for i, doc in enumerate(documents):
                    source_info = {
                        "index": i + 1,
                        "content": doc.page_content[:200] + "...",
                        "metadata": doc.metadata
                    }
                    sources.append(source_info)
            
            source_text = "\n".join([
                f"[{s['index']}] {s['metadata'].get('source', 'Unknown')}"
                for s in sources
            ]) if sources else "No sources available"
            
            # Generate response
            messages = self.response_prompt.format_messages(
                context=context,
                sources=source_text,
                question=query
            )
            
            response = self.llm.invoke(messages)
            
            return {
                "response": response.content,
                "sources": sources,
                "context": context
            }
            
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return {
                "response": "I encountered an error while generating the response. Please try again.",
                "sources": [],
                "confidence": 0.0
            }
    
    def query(
        self, 
        question: str,
        use_expansion: bool = True,
        use_reranking: bool = True,
        include_sources: bool = True
    ) -> Dict[str, Any]:
        """
        Main query method - complete RAG pipeline
        
        Args:
            question: User question
            use_expansion: Enable query expansion
            use_reranking: Enable document reranking
            include_sources: Include source references
            
        Returns:
            Complete response with answer, sources, and confidence
        """
        try:
            logger.info(f"Processing query: {question}")
            
            # Step 1: Retrieve documents
            documents, scores = self.retrieve_documents(
                query=question,
                use_expansion=use_expansion,
                use_reranking=use_reranking
            )
            
            # Step 2: Calculate confidence
            confidence = self.calculate_confidence(documents, scores)
            
            # Step 3: Generate response
            result = self.generate_response(
                query=question,
                documents=documents,
                include_sources=include_sources
            )
            
            # Add confidence and metadata
            result["confidence"] = confidence
            result["num_documents_retrieved"] = len(documents)
            result["relevance_scores"] = scores
            result["meets_threshold"] = confidence >= settings.confidence_threshold
            
            logger.info(f"Query processed successfully. Confidence: {confidence:.3f}")
            
            return result
            
        except Exception as e:
            logger.error(f"Error processing query: {e}")
            return {
                "response": "An error occurred while processing your question. Please try again.",
                "sources": [],
                "confidence": 0.0,
                "error": str(e)
            }


# Global instance
_rag_agent = None


def get_rag_agent() -> RAGAgent:
    """Get or create global RAG agent instance"""
    global _rag_agent
    if _rag_agent is None:
        _rag_agent = RAGAgent()
    return _rag_agent
