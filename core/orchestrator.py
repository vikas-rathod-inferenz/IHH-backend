"""
LangGraph Orchestration Module
Main workflow orchestration using LangGraph with multi-agent coordination
"""
import logging
import time
from typing import Dict, Any
from langgraph.graph import StateGraph, END
from langchain_core.documents import Document

from config import settings
from core.state import GraphState
from agents.guardrails import get_guardrails
from agents.rag_agent import get_rag_agent
from agents.web_search_agent import get_web_search_agent

logger = logging.getLogger(__name__)


class MedicalAssistantOrchestrator:
    """
    LangGraph-based orchestrator for medical assistant workflow
    """
    
    def __init__(self):
        """Initialize orchestrator with all agents"""
        try:
            # Initialize agents
            self.guardrails = get_guardrails()
            self.rag_agent = get_rag_agent()
            self.web_search_agent = get_web_search_agent()
            
            # Build graph
            self.graph = self._build_graph()
            
            logger.info("MedicalAssistantOrchestrator initialized")
            
        except Exception as e:
            logger.error(f"Error initializing orchestrator: {e}")
            raise
    
    def _build_graph(self) -> StateGraph:
        """Build the LangGraph workflow"""
        
        # Create workflow
        workflow = StateGraph(GraphState)
        
        # Add nodes
        workflow.add_node("input_validation", self.validate_input_node)
        workflow.add_node("agent_decision", self.agent_decision_node)
        workflow.add_node("rag_agent", self.rag_agent_node)
        workflow.add_node("web_search_agent", self.web_search_agent_node)
        workflow.add_node("combine_results", self.combine_results_node)
        workflow.add_node("output_validation", self.output_validation_node)
        workflow.add_node("human_review", self.human_review_node)
        workflow.add_node("finalize", self.finalize_node)
        
        # Set entry point
        workflow.set_entry_point("input_validation")
        
        # Add edges
        workflow.add_conditional_edges(
            "input_validation",
            self.route_after_input_validation,
            {
                "proceed": "agent_decision",
                "end": "finalize"
            }
        )
        
        workflow.add_conditional_edges(
            "agent_decision",
            self.route_to_agents,
            {
                "rag": "rag_agent",
                "web_search": "web_search_agent",
                "both": "rag_agent"
            }
        )
        
        workflow.add_conditional_edges(
            "rag_agent",
            self.route_after_rag,
            {
                "sufficient": "output_validation",
                "need_web_search": "web_search_agent",
                "end": "output_validation"
            }
        )
        
        workflow.add_edge("web_search_agent", "combine_results")
        workflow.add_edge("combine_results", "output_validation")
        
        workflow.add_conditional_edges(
            "output_validation",
            self.route_after_output_validation,
            {
                "approved": "finalize",
                "human_review": "human_review",
                "retry": "agent_decision"
            }
        )
        
        workflow.add_conditional_edges(
            "human_review",
            self.route_after_human_review,
            {
                "approved": "finalize",
                "retry": "agent_decision",
                "end": "finalize"
            }
        )
        
        workflow.add_edge("finalize", END)
        
        return workflow.compile()
    
    # Node functions
    
    def validate_input_node(self, state: GraphState) -> GraphState:
        """Validate user input using guardrails"""
        try:
            state["agent_path"].append("input_validation")
            
            is_acceptable, message = self.guardrails.check_input(state["question"])
            
            validation_result = self.guardrails.validate_input(state["question"])
            
            state["input_validated"] = is_acceptable
            state["is_medical"] = validation_result.get("is_medical", True)
            state["is_emergency"] = validation_result.get("is_emergency", False)
            state["category"] = validation_result.get("category", "medical_query")
            
            if not is_acceptable:
                state["final_response"] = message
                state["error"] = "Input validation failed"
            
            logger.info(f"Input validation: {state['category']}")
            
        except Exception as e:
            logger.error(f"Error in input validation: {e}")
            state["error"] = str(e)
        
        return state
    
    def agent_decision_node(self, state: GraphState) -> GraphState:
        """Decide which agent(s) to use"""
        try:
            state["agent_path"].append("agent_decision")
            
            # Default: try RAG first
            state["requires_rag"] = True
            state["requires_web_search"] = False
            state["current_agent"] = "rag"
            
            logger.info("Agent decision: Starting with RAG agent")
            
        except Exception as e:
            logger.error(f"Error in agent decision: {e}")
            state["error"] = str(e)
        
        return state
    
    def rag_agent_node(self, state: GraphState) -> GraphState:
        """Process query with RAG agent"""
        try:
            state["agent_path"].append("rag_agent")
            
            result = self.rag_agent.query(
                question=state["question"],
                use_expansion=True,
                use_reranking=True
            )
            
            state["rag_response"] = result.get("response", "")
            state["rag_confidence"] = result.get("confidence", 0.0)
            state["rag_sources"] = result.get("sources", [])
            state["rag_documents"] = result.get("documents", [])
            
            logger.info(f"RAG agent completed. Confidence: {state['rag_confidence']:.3f}")
            
        except Exception as e:
            logger.error(f"Error in RAG agent: {e}")
            state["rag_confidence"] = 0.0
            state["warnings"].append(f"RAG agent error: {str(e)}")
        
        return state
    
    def web_search_agent_node(self, state: GraphState) -> GraphState:
        """Process query with web search agent"""
        try:
            state["agent_path"].append("web_search_agent")
            
            result = self.web_search_agent.query(
                question=state["question"],
                max_results=5
            )
            
            state["web_search_response"] = result.get("response", "")
            state["web_search_confidence"] = result.get("confidence", 0.0)
            state["web_search_sources"] = result.get("sources", [])
            
            logger.info(f"Web search agent completed. Sources: {len(state['web_search_sources'])}")
            
        except Exception as e:
            logger.error(f"Error in web search agent: {e}")
            state["web_search_confidence"] = 0.0
            state["warnings"].append(f"Web search agent error: {str(e)}")
        
        return state
    
    def combine_results_node(self, state: GraphState) -> GraphState:
        """Combine results from multiple agents"""
        try:
            state["agent_path"].append("combine_results")
            
            # Combine responses
            responses = []
            sources = []
            confidences = []
            
            if state.get("rag_response"):
                responses.append(f"**From Knowledge Base:**\n{state['rag_response']}")
                sources.extend(state.get("rag_sources", []))
                confidences.append(state.get("rag_confidence", 0.0))
            
            if state.get("web_search_response"):
                responses.append(f"\n\n**From Recent Research:**\n{state['web_search_response']}")
                sources.extend(state.get("web_search_sources", []))
                confidences.append(state.get("web_search_confidence", 0.0))
            
            state["final_response"] = "\n\n".join(responses)
            state["final_sources"] = sources
            state["final_confidence"] = sum(confidences) / len(confidences) if confidences else 0.0
            
            logger.info("Results combined successfully")
            
        except Exception as e:
            logger.error(f"Error combining results: {e}")
            state["error"] = str(e)
        
        return state
    
    def output_validation_node(self, state: GraphState) -> GraphState:
        """Validate output using guardrails"""
        try:
            state["agent_path"].append("output_validation")
            
            # Use RAG response if only RAG, otherwise use combined
            response_to_validate = state.get("final_response") or state.get("rag_response", "")
            
            is_acceptable, modified_response, message = self.guardrails.check_output(
                question=state["question"],
                response=response_to_validate
            )
            
            state["output_validated"] = is_acceptable
            
            if is_acceptable:
                state["final_response"] = modified_response
                if not state.get("final_sources"):
                    state["final_sources"] = state.get("rag_sources", [])
                if not state.get("final_confidence"):
                    state["final_confidence"] = state.get("rag_confidence", 0.0)
            else:
                state["error"] = "Output validation failed"
            
            # Check if human review is needed (low confidence)
            if state.get("final_confidence", 0.0) < settings.confidence_threshold:
                state["requires_human_review"] = True
                state["warnings"].append("Low confidence - flagged for human review")
            
            logger.info(f"Output validation: {'approved' if is_acceptable else 'rejected'}")
            
        except Exception as e:
            logger.error(f"Error in output validation: {e}")
            state["error"] = str(e)
        
        return state
    
    def human_review_node(self, state: GraphState) -> GraphState:
        """Human-in-the-loop review (placeholder for actual implementation)"""
        try:
            state["agent_path"].append("human_review")
            
            # In production, this would pause and wait for human input
            # For now, we'll mark it as pending review
            state["warnings"].append("Human review required - low confidence response")
            
            # Add disclaimer
            disclaimer = "\n\n⚠️ **Notice:** This response has been flagged for expert review due to lower confidence. Please use with caution and consult a healthcare professional."
            state["final_response"] = state.get("final_response", "") + disclaimer
            
            logger.info("Human review node - flagged for review")
            
        except Exception as e:
            logger.error(f"Error in human review: {e}")
            state["error"] = str(e)
        
        return state
    
    def finalize_node(self, state: GraphState) -> GraphState:
        """Finalize response and calculate processing time"""
        try:
            state["agent_path"].append("finalize")
            
            # Ensure we have a final response
            if not state.get("final_response"):
                state["final_response"] = "I apologize, but I couldn't generate a response. Please try rephrasing your question."
            
            logger.info("Response finalized")
            
        except Exception as e:
            logger.error(f"Error in finalize: {e}")
            state["error"] = str(e)
        
        return state
    
    # Routing functions
    
    def route_after_input_validation(self, state: GraphState) -> str:
        """Route after input validation"""
        if not state.get("input_validated", False):
            return "end"
        return "proceed"
    
    def route_to_agents(self, state: GraphState) -> str:
        """Route to appropriate agent(s)"""
        if state.get("requires_rag", True):
            return "rag"
        elif state.get("requires_web_search", False):
            return "web_search"
        return "rag"
    
    def route_after_rag(self, state: GraphState) -> str:
        """Route after RAG agent based on confidence"""
        confidence = state.get("rag_confidence", 0.0)
        
        if confidence >= settings.confidence_threshold:
            return "sufficient"
        else:
            # Low confidence - try web search
            logger.info("Low RAG confidence - routing to web search")
            return "need_web_search"
    
    def route_after_output_validation(self, state: GraphState) -> str:
        """Route after output validation"""
        if not state.get("output_validated", False):
            return "retry" if not state.get("requires_retry", False) else "end"
        
        if state.get("requires_human_review", False):
            return "human_review"
        
        return "approved"
    
    def route_after_human_review(self, state: GraphState) -> str:
        """Route after human review"""
        if state.get("human_approved", None):
            return "approved"
        elif state.get("requires_retry", False):
            return "retry"
        return "end"
    
    # Main execution
    
    def process_query(self, question: str, user_id: str = None, session_id: str = None) -> Dict[str, Any]:
        """
        Process a user query through the workflow
        
        Args:
            question: User question
            user_id: Optional user ID
            session_id: Optional session ID
            
        Returns:
            Complete response dictionary
        """
        try:
            start_time = time.time()
            
            # Initialize state
            initial_state: GraphState = {
                "question": question,
                "user_id": user_id,
                "session_id": session_id,
                "input_validated": False,
                "is_medical": True,
                "is_emergency": False,
                "category": "unknown",
                "current_agent": None,
                "requires_rag": False,
                "requires_web_search": False,
                "requires_human_review": False,
                "rag_documents": [],
                "rag_response": None,
                "rag_confidence": 0.0,
                "rag_sources": [],
                "web_search_response": None,
                "web_search_sources": [],
                "web_search_confidence": 0.0,
                "image_path": None,
                "image_analysis": None,
                "final_response": "",
                "final_sources": [],
                "final_confidence": 0.0,
                "output_validated": False,
                "human_feedback": None,
                "human_approved": None,
                "requires_retry": False,
                "error": None,
                "warnings": [],
                "processing_time": 0.0,
                "agent_path": []
            }
            
            # Execute graph
            final_state = self.graph.invoke(initial_state)
            
            # Calculate processing time
            processing_time = time.time() - start_time
            final_state["processing_time"] = processing_time
            
            # Build response
            response = {
                "response": final_state.get("final_response", ""),
                "sources": final_state.get("final_sources", []),
                "confidence": final_state.get("final_confidence", 0.0),
                "category": final_state.get("category", "unknown"),
                "agent_path": final_state.get("agent_path", []),
                "processing_time": processing_time,
                "warnings": final_state.get("warnings", []),
                "error": final_state.get("error")
            }
            
            logger.info(f"Query processed in {processing_time:.2f}s via {' -> '.join(response['agent_path'])}")
            
            return response
            
        except Exception as e:
            logger.error(f"Error processing query: {e}")
            return {
                "response": "An error occurred while processing your question. Please try again.",
                "sources": [],
                "confidence": 0.0,
                "error": str(e)
            }


# Global instance
_orchestrator = None


def get_orchestrator() -> MedicalAssistantOrchestrator:
    """Get or create global orchestrator instance"""
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = MedicalAssistantOrchestrator()
    return _orchestrator
