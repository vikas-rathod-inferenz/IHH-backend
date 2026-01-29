"""
Web Search Agent Module
Performs web searches and processes results for medical queries
"""
import logging
from typing import List, Dict, Any
from langchain_openai import AzureChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from config import settings
from agents.web_search_agent.tavily_search import get_tavily_search

logger = logging.getLogger(__name__)


class WebSearchAgent:
    """
    Agent that performs web searches and synthesizes medical information
    """
    
    def __init__(self):
        """Initialize web search agent"""
        try:
            # Initialize LLM
            self.llm = AzureChatOpenAI(
                azure_endpoint=settings.azure_endpoint,
                openai_api_key=settings.openai_api_key,
                openai_api_version=settings.openai_api_version,
                deployment_name=settings.deployment_name or settings.model_name,
                temperature=settings.temperature,
                max_tokens=settings.max_tokens
            )
            
            # Initialize search client
            self.search_client = get_tavily_search()
            
            # Create synthesis prompt
            self.synthesis_prompt = ChatPromptTemplate.from_messages([
                ("system", """You are a medical research analyst. Synthesize information from multiple web sources to answer the user's medical question.

Guidelines:
1. Combine information from all provided sources
2. Cite sources using [1], [2], etc.
3. Prioritize recent research and reputable medical sources
4. Acknowledge any conflicting information
5. Provide balanced, evidence-based responses
6. Always recommend consulting healthcare professionals

Search Results:
{search_results}"""),
                ("human", "{question}")
            ])
            
            logger.info("WebSearchAgent initialized")
            
        except Exception as e:
            logger.error(f"Error initializing WebSearchAgent: {e}")
            raise
    
    def search(self, query: str, max_results: int = 5) -> List[Dict[str, Any]]:
        """
        Perform web search
        
        Args:
            query: Search query
            max_results: Maximum results to return
            
        Returns:
            List of search results
        """
        try:
            results = self.search_client.medical_search(
                query=query,
                max_results=max_results
            )
            logger.info(f"Web search completed: {len(results)} results")
            return results
        except Exception as e:
            logger.error(f"Error in web search: {e}")
            return []
    
    def synthesize_results(
        self, 
        query: str, 
        search_results: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Synthesize search results into coherent response
        
        Args:
            query: User query
            search_results: List of search results
            
        Returns:
            Synthesized response with sources
        """
        try:
            if not search_results:
                return {
                    "response": "I couldn't find recent information about this topic. Please try rephrasing your question or consult a healthcare professional.",
                    "sources": [],
                    "confidence": 0.0
                }
            
            # Format search results for LLM
            formatted_results = "\n\n".join([
                f"[Source {i+1}]\nTitle: {result['title']}\nURL: {result['url']}\nContent: {result['content']}"
                for i, result in enumerate(search_results)
            ])
            
            # Generate synthesis
            messages = self.synthesis_prompt.format_messages(
                search_results=formatted_results,
                question=query
            )
            
            response = self.llm.invoke(messages)
            
            # Prepare sources
            sources = [
                {
                    "index": i + 1,
                    "title": result["title"],
                    "url": result["url"],
                    "published_date": result.get("published_date", "")
                }
                for i, result in enumerate(search_results)
            ]
            
            return {
                "response": response.content,
                "sources": sources,
                "num_sources": len(sources),
                "confidence": 0.8  # High confidence for web search
            }
            
        except Exception as e:
            logger.error(f"Error synthesizing results: {e}")
            return {
                "response": "An error occurred while processing search results.",
                "sources": [],
                "confidence": 0.0,
                "error": str(e)
            }
    
    def query(self, question: str, max_results: int = 5) -> Dict[str, Any]:
        """
        Complete web search pipeline
        
        Args:
            question: User question
            max_results: Maximum search results
            
        Returns:
            Complete response with answer and sources
        """
        try:
            logger.info(f"Processing web search query: {question}")
            
            # Step 1: Perform search
            search_results = self.search(
                query=question,
                max_results=max_results
            )
            
            # Step 2: Synthesize results
            result = self.synthesize_results(
                query=question,
                search_results=search_results
            )
            
            logger.info(f"Web search query processed. Sources: {result.get('num_sources', 0)}")
            
            return result
            
        except Exception as e:
            logger.error(f"Error processing web search query: {e}")
            return {
                "response": "An error occurred during web search. Please try again.",
                "sources": [],
                "confidence": 0.0,
                "error": str(e)
            }


# Global instance
_web_search_agent = None


def get_web_search_agent() -> WebSearchAgent:
    """Get or create global web search agent instance"""
    global _web_search_agent
    if _web_search_agent is None:
        _web_search_agent = WebSearchAgent()
    return _web_search_agent
