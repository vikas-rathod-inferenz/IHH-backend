"""
Query Expansion Module
Expands user queries with medical domain terms for better retrieval
"""
import logging
from typing import List
from langchain_openai import AzureChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from config import settings

logger = logging.getLogger(__name__)


class QueryExpander:
    """
    Expands user queries with related medical terms and concepts
    """
    
    def __init__(self):
        """Initialize query expander with LLM"""
        self.llm = AzureChatOpenAI(
            azure_endpoint=settings.azure_endpoint,
            openai_api_key=settings.openai_api_key,
            openai_api_version=settings.openai_api_version,
            deployment_name=settings.deployment_name or settings.model_name,
            temperature=0.3,
            max_tokens=500
        )
        
        self.expansion_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a medical terminology expert. Given a user query, generate related medical terms, 
            synonyms, and relevant concepts that would help retrieve comprehensive information.
            
            Return ONLY a comma-separated list of terms (including the original query terms).
            Keep it concise - maximum 10 terms.
            
            Example:
            Query: "headache treatment"
            Response: headache, migraine, cephalalgia, analgesics, pain relief, NSAIDs, tension headache, cluster headache"""),
            ("human", "Query: {query}\nResponse:")
        ])
        
        logger.info("QueryExpander initialized")
    
    def expand_query(self, query: str) -> List[str]:
        """
        Expand query with related medical terms
        
        Args:
            query: Original user query
            
        Returns:
            List of expanded query terms
        """
        try:
            messages = self.expansion_prompt.format_messages(query=query)
            response = self.llm.invoke(messages)
            
            # Parse comma-separated terms
            expanded_terms = [term.strip() for term in response.content.split(",")]
            
            logger.info(f"Expanded query '{query}' to {len(expanded_terms)} terms")
            return expanded_terms
            
        except Exception as e:
            logger.error(f"Error expanding query: {e}")
            # Return original query if expansion fails
            return [query]
    
    def create_expanded_query(self, query: str) -> str:
        """
        Create a single expanded query string
        
        Args:
            query: Original user query
            
        Returns:
            Expanded query string
        """
        try:
            terms = self.expand_query(query)
            expanded_query = " ".join(terms)
            return expanded_query
        except Exception as e:
            logger.error(f"Error creating expanded query: {e}")
            return query


# Global instance
_query_expander = None


def get_query_expander() -> QueryExpander:
    """Get or create global query expander instance"""
    global _query_expander
    if _query_expander is None:
        _query_expander = QueryExpander()
    return _query_expander
