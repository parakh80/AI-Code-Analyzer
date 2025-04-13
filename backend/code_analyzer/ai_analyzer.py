import os
import time
from typing import Dict, List, Any
from google import genai
from dotenv import load_dotenv
import logging

logger = logging.getLogger(__name__)

class AIAnalyzer:
    def __init__(self):
        load_dotenv()
        self.client = genai.Client(api_key=os.getenv('GEMINI_API_KEY'))
        self.model = "gemini-2.0-flash"  # Using the latest model
        self.max_retries = 3
        self.initial_retry_delay = 1  # seconds
        self.chat = None  # Will be initialized for multi-turn conversations

    def _create_prompt(self, code: str, context: Dict[str, Any], analysis_type: str) -> str:
        """Create a specialized prompt for the LLM based on analysis type."""
        # Determine the language from the context
        language = context.get('language', 'python').lower()
        
        base_prompt = f"""
        You are an expert code analyzer specializing in correctness assessment and semantic understanding.
        Analyze the following {language} code and provide a detailed assessment.
        
        Code context: {context}
        Code:
        {code}
        """

        if analysis_type == "semantic_understanding":
            return f"""
            {base_prompt}
            
            Analyze the code's semantic meaning and intent:
            1. What is the primary purpose and goal of this code?
            2. What are the key algorithms or patterns being used?
            3. What assumptions is the code making about its inputs and environment?
            4. What are the expected outputs and their formats?
            5. Are there any implicit requirements or constraints?
            
            Provide a detailed explanation of the code's semantic meaning and how it achieves its goals.
            """
        elif analysis_type == "correctness_assessment":
            return f"""
            {base_prompt}
            
            Evaluate the code's correctness and potential issues:
            1. Are there any logical flaws or incorrect assumptions?
            2. Does the code handle all expected input cases correctly?
            3. Are there any potential race conditions or concurrency issues?
            4. Does the code properly validate inputs and handle errors?
            5. Are there any security vulnerabilities or unsafe practices?
            
            Provide a detailed assessment of the code's correctness and potential issues.
            """
        elif analysis_type == "edge_cases":
            return f"""
            {base_prompt}
            
            Identify potential edge cases and boundary conditions:
            1. What are the extreme or unusual input values that could cause issues?
            2. How does the code handle empty or null inputs?
            3. What happens with very large or very small values?
            4. Are there any timing or resource constraints that could cause problems?
            5. What happens in concurrent or parallel execution scenarios?
            
            List all potential edge cases and explain how the code handles them.
            """
        elif analysis_type == "test_cases":
            # Customize test cases based on language
            if language == "javascript":
                return f"""
                {base_prompt}
                
                Generate comprehensive JavaScript test cases:
                1. Normal use cases with typical inputs
                2. Edge cases and boundary conditions
                3. Error conditions and invalid inputs
                4. Performance test cases
                5. Security test cases
                
                Format the tests as JavaScript code using a modern testing framework like Jest or Mocha.
                """
            else:  # python or other languages
                return f"""
                {base_prompt}
                
                Generate comprehensive test cases:
                1. Normal use cases with typical inputs
                2. Edge cases and boundary conditions
                3. Error conditions and invalid inputs
                4. Performance test cases
                5. Security test cases
                
                Format the tests appropriately for the {language} language.
                """
        else:
            raise ValueError(f"Unknown analysis type: {analysis_type}")

    def _make_api_call(self, prompt: str, retry_count: int = 0) -> Dict[str, Any]:
        """Make API call with retry logic."""
        try:
            # Initialize chat if not already done
            if self.chat is None:
                logger.debug("Initializing new chat session with Gemini.")
                # REMOVE the timeout argument from this call
                self.chat = self.client.chats.create(
                    model=self.model
                    # No 'timeout=...' here
                )
                logger.debug("Chat session initialized.")

            logger.debug(f"Sending prompt to Gemini (attempt {retry_count + 1}):\n{prompt[:200]}...") # Log truncated prompt
            # Also ensure timeout is not used here if the library doesn't support it for send_message
            response = self.chat.send_message(
                prompt
                # No 'timeout=...' here either, unless the specific method supports it
            )
            logger.debug("Received response from Gemini.")

            return {
                'success': True,
                'content': response.text
            }
        except Exception as e:
            logger.warning(f"API call failed (attempt {retry_count + 1}/{self.max_retries}): {str(e)}")
            if retry_count < self.max_retries:
                delay = self.initial_retry_delay * (2 ** retry_count)
                logger.warning(f"Retrying in {delay} seconds...")
                time.sleep(delay)
                # Reset chat object to force re-initialization on next attempt if create failed
                if "Chats.create()" in str(e):
                    self.chat = None
                return self._make_api_call(prompt, retry_count + 1)
            else:
                logger.error(f"Max retries reached. Final error: {str(e)}")
                # Ensure self.chat is reset if the error occurred during creation
                if "Chats.create()" in str(e):
                    self.chat = None
                return {
                    'success': False,
                    'error': f"Max retries reached: {str(e)}" # Include the error message
                }

    def analyze_code(self, code_chunk: Dict[str, Any], analysis_type: str) -> Dict[str, Any]:
        """Analyze a code chunk using the specified analysis type."""
        prompt = self._create_prompt(code_chunk['code'], code_chunk['context'], analysis_type)
        
        try:
            logger.info(f"Making API call for {analysis_type} analysis")
            result = self._make_api_call(prompt)
            
            if result['success']:
                return {
                    'analysis_type': analysis_type,
                    'code_context': code_chunk['context'],
                    'response': result['content']
                }
            else:
                return {
                    'analysis_type': analysis_type,
                    'code_context': code_chunk['context'],
                    'error': result['error']
                }
        except Exception as e:
            logger.error(f"Analysis failed: {str(e)}")
            return {
                'analysis_type': analysis_type,
                'code_context': code_chunk['context'],
                'error': str(e)
            }

    def analyze_semantics(self, code_chunk: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze the semantic meaning and intent of the code."""
        return self.analyze_code(code_chunk, "semantic_understanding")

    def assess_correctness(self, code_chunk: Dict[str, Any]) -> Dict[str, Any]:
        """Assess the code's correctness and identify potential issues."""
        return self.analyze_code(code_chunk, "correctness_assessment")

    def identify_edge_cases(self, code_chunk: Dict[str, Any]) -> Dict[str, Any]:
        """Identify potential edge cases and boundary conditions."""
        return self.analyze_code(code_chunk, "edge_cases")

    def generate_test_cases(self, code_chunk: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive test cases for the code."""
        return self.analyze_code(code_chunk, "test_cases")