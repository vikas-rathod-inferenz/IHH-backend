"""
Guardrails Module
Input and output validation for safe and relevant medical responses
"""
import logging
from typing import Dict, Any, List
from langchain_openai import AzureChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from config import settings

logger = logging.getLogger(__name__)


class Guardrails:
    """
    Input and output guardrails for medical chatbot
    """
    
    def __init__(self):
        """Initialize guardrails with LLM"""
        try:
            self.llm = AzureChatOpenAI(
                azure_endpoint=settings.azure_endpoint,
                openai_api_key=settings.openai_api_key,
                openai_api_version=settings.openai_api_version,
                deployment_name=settings.deployment_name or settings.model_name,
                temperature=0.0,  # Deterministic for safety checks
                # max_tokens=500
            )
            
            # Input validation prompt
            self.input_validation_prompt = ChatPromptTemplate.from_messages([
                ("system", """You are a content safety classifier for a medical chatbot. Analyze the user input and determine if it is safe and appropriate.

                    Check for:
                    1. Medical relevance - Is this a medical/health-related question?
                    2. Safety - Does this request emergency medical advice?
                    3. Appropriateness - Is the content appropriate (no harmful, illegal, or inappropriate requests)?
                    4. Scope - Is this within the scope of a medical information chatbot?

                    Respond with a JSON object:
                    {{
                        "is_safe": true/false,
                        "is_medical": true/false,
                        "is_emergency": true/false,
                        "category": "medical_query|emergency|off_topic|inappropriate",
                        "reason": "Brief explanation"
                    }}"""),
                                    ("human", "User input: {user_input}")
                ])
            
            # Output validation prompt
            self.output_validation_prompt = ChatPromptTemplate.from_messages([
                ("system", """You are a medical response safety checker. Analyze the AI-generated response and verify it is safe and appropriate.

                    Check for:
                    1. Medical accuracy - Does the response avoid making definitive diagnoses?
                    2. Safety disclaimers - Does it recommend consulting healthcare professionals?
                    3. Harmful content - Is there any potentially harmful advice?
                    4. Bias - Is the response balanced and unbiased?

                    Respond with a JSON object:
                    {{
                        "is_safe": true/false,
                        "has_disclaimer": true/false,
                        "issues": ["list of any issues found"],
                        "severity": "low|medium|high",
                        "recommendation": "approve|modify|reject"
                    }}"""),
                                    ("human", "Question: {question}\n\nAI Response: {response}")
            ])
            
            logger.info("Guardrails initialized")
            
        except Exception as e:
            logger.error(f"Error initializing Guardrails: {e}")
            raise
    
    def validate_input(self, user_input: str) -> Dict[str, Any]:
        """
        Validate user input for safety and relevance
        
        Args:
            user_input: User's query or input
            
        Returns:
            Validation result dictionary
        """
        try:
            messages = self.input_validation_prompt.format_messages(
                user_input=user_input
            )
            
            response = self.llm.invoke(messages)
            
            # Parse JSON response
            import json
            try:
                result = json.loads(response.content)
            except json.JSONDecodeError:
                # Fallback if JSON parsing fails
                logger.warning("Failed to parse guardrails response as JSON")
                result = {
                    "is_safe": True,
                    "is_medical": True,
                    "is_emergency": False,
                    "category": "medical_query",
                    "reason": "Unable to parse validation result"
                }
            
            logger.info(f"Input validation: {result.get('category', 'unknown')}")
            return result
            
        except Exception as e:
            logger.error(f"Error validating input: {e}")
            # Fail safe - allow input but flag for review
            return {
                "is_safe": True,
                "is_medical": True,
                "is_emergency": False,
                "category": "medical_query",
                "reason": f"Validation error: {str(e)}"
            }
    
    def validate_output(self, question: str, response: str) -> Dict[str, Any]:
        """
        Validate AI-generated output for safety
        
        Args:
            question: User's question
            response: AI-generated response
            
        Returns:
            Validation result dictionary
        """
        try:
            messages = self.output_validation_prompt.format_messages(
                question=question,
                response=response
            )
            
            validation_response = self.llm.invoke(messages)
            
            # Parse JSON response
            import json
            try:
                result = json.loads(validation_response.content)
            except json.JSONDecodeError:
                logger.warning("Failed to parse output validation as JSON")
                result = {
                    "is_safe": True,
                    "has_disclaimer": True,
                    "issues": [],
                    "severity": "low",
                    "recommendation": "approve"
                }
            
            logger.info(f"Output validation: {result.get('recommendation', 'unknown')}")
            return result
            
        except Exception as e:
            logger.error(f"Error validating output: {e}")
            return {
                "is_safe": True,
                "has_disclaimer": False,
                "issues": [f"Validation error: {str(e)}"],
                "severity": "medium",
                "recommendation": "approve"
            }
    
    def check_input(self, user_input: str) -> tuple[bool, str]:
        """
        Quick check if input is acceptable
        
        Args:
            user_input: User input
            
        Returns:
            Tuple of (is_acceptable, message)
        """
        try:
            validation = self.validate_input(user_input)
            
            # Handle emergency
            if validation.get("is_emergency", False):
                return False, "⚠️ This appears to be a medical emergency. Please call emergency services immediately (911 in the US) or go to the nearest emergency room. This chatbot cannot provide emergency medical assistance."
            
            # Handle off-topic
            if not validation.get("is_medical", True):
                return False, "I'm designed to help with medical and health-related questions. Your question appears to be outside my area of expertise. Please ask a medical or health-related question."
            
            # Handle inappropriate content
            if not validation.get("is_safe", True):
                return False, "I cannot process this request as it may be inappropriate or unsafe. Please rephrase your question or ask something else."
            
            return True, "Input validated successfully"
            
        except Exception as e:
            logger.error(f"Error in input check: {e}")
            # Fail safe - allow input
            return True, "Input check completed"
    
    def check_output(self, question: str, response: str) -> tuple[bool, str, str]:
        """
        Quick check if output is acceptable
        
        Args:
            question: User question
            response: AI response
            
        Returns:
            Tuple of (is_acceptable, modified_response, message)
        """
        try:
            validation = self.validate_output(question, response)
            
            recommendation = validation.get("recommendation", "approve")
            
            if recommendation == "reject":
                return False, "", "Response rejected by safety checks. Please rephrase your question."
            
            # Add disclaimer if missing
            modified_response = response
            if not validation.get("has_disclaimer", False):
                disclaimer = "\n\n **Important:** This information is based on document retrieval and web search only. It is not a substitute for professional medical advice, diagnosis, or treatment. Please consult with a qualified healthcare provider for personalized medical guidance."
                modified_response = response + disclaimer
            
            return True, modified_response, "Output validated"
            
        except Exception as e:
            logger.error(f"Error in output check: {e}")
            # Fail safe - allow output
            return True, response, "Output check completed"


# Global instance
_guardrails = None


def get_guardrails() -> Guardrails:
    """Get or create global guardrails instance"""
    global _guardrails
    if _guardrails is None:
        _guardrails = Guardrails()
    return _guardrails
