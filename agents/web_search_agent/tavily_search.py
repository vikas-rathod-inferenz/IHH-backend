"""
Tavily Web Search Module
Performs real-time web searches for medical information
"""
import logging
from typing import List, Dict, Any, Optional
from tavily import TavilyClient
from config import settings

logger = logging.getLogger(__name__)


class TavilySearch:
    """
    Wrapper for Tavily API to search medical information
    """
    
    def __init__(self):
        """Initialize Tavily client"""
        try:
            self.client = TavilyClient(api_key=settings.tavily_api_key)
            logger.info("TavilySearch initialized")
        except Exception as e:
            logger.error(f"Error initializing TavilySearch: {e}")
            raise
    
    def search(
        self,
        query: str,
        max_results: int = 5,
        search_depth: str = "advanced",
        include_domains: Optional[List[str]] = None,
        exclude_domains: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Perform web search using Tavily
        
        Args:
            query: Search query
            max_results: Maximum number of results
            search_depth: "basic" or "advanced"
            include_domains: List of domains to include
            exclude_domains: List of domains to exclude
            
        Returns:
            Search results dictionary
        """
        try:
            # Medical-focused domains
            if include_domains is None:
                include_domains = [
                    "pubmed.ncbi.nlm.nih.gov",
                    "nih.gov",
                    "mayoclinic.org",
                    "who.int",
                    "cdc.gov",
                    "nature.com",
                    "thelancet.com",
                    "nejm.org"
                ]
            
            response = self.client.search(
                query=query,
                max_results=max_results,
                search_depth=search_depth,
                include_domains=include_domains,
                exclude_domains=exclude_domains
            )
            
            logger.info(f"Tavily search completed: {len(response.get('results', []))} results")
            return response
            
        except Exception as e:
            logger.error(f"Error performing Tavily search: {e}")
            return {"results": [], "error": str(e)}
    
    def medical_search(self, query: str, max_results: int = 5) -> List[Dict[str, Any]]:
        """
        Perform medical-focused search
        
        Args:
            query: Medical query
            max_results: Maximum results
            
        Returns:
            List of search results
        """
        try:
            # Add medical context to query
            medical_query = f"medical research {query}"
            
            response = self.search(
                query=medical_query,
                max_results=max_results,
                search_depth="advanced"
            )
            
            results = response.get("results", [])
            
            # Format results
            formatted_results = []
            for result in results:
                formatted_results.append({
                    "title": result.get("title", ""),
                    "url": result.get("url", ""),
                    "content": result.get("content", ""),
                    "score": result.get("score", 0.0),
                    "published_date": result.get("published_date", "")
                })
            
            return formatted_results
            
        except Exception as e:
            logger.error(f"Error in medical search: {e}")
            return []


# Global instance
_tavily_search = None


def get_tavily_search() -> TavilySearch:
    """Get or create global Tavily search instance"""
    global _tavily_search
    if _tavily_search is None:
        _tavily_search = TavilySearch()
    return _tavily_search
