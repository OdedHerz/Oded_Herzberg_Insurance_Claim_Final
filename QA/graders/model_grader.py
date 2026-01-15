"""
Model-Based Grader for QA Testing Suite

Uses Gemini (Google AI) as an LLM judge to evaluate answer quality
on subjective criteria like accuracy, completeness, and coherence.
"""

import json
import os
import sys
from pathlib import Path
from typing import Dict, List, Any
import time

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent))

from Config import config
from openai import OpenAI
import os


class ModelGrader:
    """
    Applies model-based grading using OpenAI as LLM judge.
    
    Used for:
    - Needle Agent: Evaluate factual accuracy, completeness, precision
    - Summary Agent: Evaluate comprehensiveness, coherence, synthesis quality
    """
    
    def __init__(self, use_openai: bool = True):
        """
        Initialize the model grader.
        
        Args:
            use_openai: If True, uses OpenAI (default). If False, uses Gemini.
        """
        self.use_openai = use_openai
        
        if use_openai:
            # Initialize OpenAI
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise ValueError("OPENAI_API_KEY not found in environment variables")
            
            self.client = OpenAI(api_key=api_key)
            self.model_name = "gpt-4o-mini"  # Fast and cost-effective
            # Alternative: "gpt-4o" for higher quality but more expensive
            
            print(f"[MODEL GRADER] Initialized with OpenAI {self.model_name}")
        else:
            # Initialize Gemini (fallback)
            try:
                import google.generativeai as genai
            except ImportError:
                raise ImportError("google-generativeai package not installed. Run: pip install google-generativeai")
            
            api_key = config.GOOGLE_AI_API_KEY
            if not api_key:
                raise ValueError("GOOGLE_AI_API_KEY not found in environment variables")
            
            genai.configure(api_key=api_key)
            self.model_name = config.GEMINI_MODEL
            self.model = genai.GenerativeModel(self.model_name)
            
            print(f"[MODEL GRADER] Initialized with Gemini {self.model_name}")
    
    def _call_llm(self, prompt: str) -> str:
        """
        Call the LLM (OpenAI or Gemini) with the given prompt.
        
        Args:
            prompt: The prompt to send to the LLM
            
        Returns:
            str: The LLM's response text
        """
        if self.use_openai:
            # Call OpenAI
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": "You are an expert evaluator grading AI agent responses. Return only valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=1000,
                response_format={"type": "json_object"}  # Force JSON output
            )
            return response.choices[0].message.content.strip()
        else:
            # Call Gemini
            import google.generativeai as genai
            
            safety_settings = [
                {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
            ]
            
            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.1,
                    max_output_tokens=1000
                ),
                safety_settings=safety_settings
            )
            
            # Check if response was blocked
            if not response.parts:
                raise ValueError("Response blocked by safety filters")
            
            return response.text.strip()
    
    def _sanitize_json_response(self, text: str) -> str:
        """
        Sanitize JSON response from Gemini by removing/escaping problematic characters.
        
        Args:
            text: Raw JSON text from Gemini
            
        Returns:
            str: Sanitized JSON text that can be parsed
        """
        # Replace literal newlines within string values with spaces
        result = []
        in_string = False
        escape_next = False
        
        for char in text:
            if escape_next:
                result.append(char)
                escape_next = False
                continue
            
            if char == '\\':
                escape_next = True
                result.append(char)
                continue
            
            if char == '"':
                in_string = not in_string
                result.append(char)
                continue
            
            if in_string and char in ('\n', '\r'):
                result.append(' ')  # Replace newline/carriage return with space
            else:
                result.append(char)
        
        return ''.join(result)
    
    def _parse_json_response(self, response_text: str, test_id: str) -> dict:
        """
        Parse JSON response from Gemini with error handling.
        
        Args:
            response_text: JSON text from Gemini
            test_id: Test ID for error messages
            
        Returns:
            dict: Parsed JSON scores
            
        Raises:
            json.JSONDecodeError: If parsing fails after all attempts
        """
        import re
        
        # Remove markdown code blocks if present
        if '```json' in response_text:
            start = response_text.find('```json') + 7
            end = response_text.find('```', start)
            if end > start:
                response_text = response_text[start:end].strip()
        elif response_text.startswith('```'):
            parts = response_text.split('```')
            if len(parts) >= 2:
                response_text = parts[1]
                if response_text.startswith('json'):
                    response_text = response_text[4:]
            response_text = response_text.strip()
        
        # Sanitize JSON (fix newlines in strings)
        response_text = self._sanitize_json_response(response_text)
        
        # Try to parse JSON
        try:
            return json.loads(response_text)
        except json.JSONDecodeError as e:
            print(f"[WARNING] JSON parse error for {test_id}, attempting fixes...")
            
            # Try to fix common issues
            try:
                # Remove trailing commas
                response_text = re.sub(r',\s*}', '}', response_text)
                response_text = re.sub(r',\s*]', ']', response_text)
                return json.loads(response_text)
            except json.JSONDecodeError:
                # Last resort: extract JSON object
                print(f"[ERROR] Could not parse JSON for {test_id}")
                print(f"[DEBUG] Response (first 300 chars): {response_text[:300]}")
                raise e
    
    def grade_needle_test(self, test: Dict[str, Any], answer: str) -> Dict[str, Any]:
        """
        Grade a needle agent test using Gemini LLM judge.
        
        Evaluates: factual accuracy, completeness, precision, no hallucination
        
        Args:
            test: Test case with question and ground truth
            answer: Agent's answer string
            
        Returns:
            dict: Grading results with scores and reasoning
        """
        question = test['question']
        ground_truth = test.get('ground_truth', '')
        criteria = test.get('model_grader_criteria', ['factual_accuracy', 'completeness', 'precision'])
        
        prompt = f"""You are evaluating an AI agent's answer to a factual question about an insurance claim.

Question: {question}

Ground Truth Answer: {ground_truth}

Agent's Answer: {answer}

Evaluate the agent's answer on the following criteria (score each from 0.0 to 1.0):

1. **Factual Accuracy**: Are all facts in the agent's answer correct when compared to the ground truth?
   - 1.0: All facts are accurate
   - 0.5: Some facts are accurate, some are wrong or missing
   - 0.0: Facts are incorrect or completely wrong

2. **Completeness**: Does the answer include all key information from the ground truth?
   - 1.0: All key information present
   - 0.5: Some key information present, some missing
   - 0.0: Missing most or all key information

3. **Precision**: Are specific details (numbers, names, dates, times) stated precisely?
   - 1.0: All specific details are precise and correct
   - 0.5: Some details are precise, some are vague or approximate
   - 0.0: Details are vague, approximate, or incorrect

4. **No Hallucination**: Does the answer only include information that could reasonably come from the source?
   - 1.0: No hallucinated information
   - 0.5: Minor additions that are reasonable inferences
   - 0.0: Contains fabricated or hallucinated information

Return ONLY a valid, complete JSON object with this exact structure (no markdown, no code blocks, keep reasoning under 50 words):
{{
  "factual_accuracy": <score 0.0-1.0>,
  "completeness": <score 0.0-1.0>,
  "precision": <score 0.0-1.0>,
  "no_hallucination": <score 0.0-1.0>,
  "overall_score": <average of all scores>,
  "reasoning": "<brief 1-2 sentence explanation>"
}}"""
        
        try:
            # Call LLM (OpenAI or Gemini) using helper method
            try:
                response_text = self._call_llm(prompt)
            except ValueError as e:
                # Handle blocked responses (Gemini safety filters)
                if "blocked by safety filters" in str(e):
                    print(f"[WARNING] LLM blocked response for {test['id']} (safety filters)")
                    return {
                        'test_id': test['id'],
                        'test_type': 'needle',
                        'model_used': self.model_name,
                        'scores': {
                            'factual_accuracy': 0.0,
                            'completeness': 0.0,
                            'precision': 0.0,
                            'no_hallucination': 0.0,
                            'overall_score': 0.0
                        },
                        'overall_score': 0.0,
                        'reasoning': 'Response blocked by safety filters',
                        'blocked': True
                    }
                else:
                    raise
            
            # Parse JSON response using helper method
            scores = self._parse_json_response(response_text, test['id'])
            
            # Build result
            result = {
                'test_id': test['id'],
                'test_type': 'needle',
                'model_used': self.model_name,
                'scores': scores,
                'overall_score': scores.get('overall_score', 0.0),
                'reasoning': scores.get('reasoning', ''),
                'criteria_evaluated': list(scores.keys())
            }
            
            return result
            
        except Exception as e:
            print(f"[ERROR] Model grading failed for {test['id']}: {e}")
            return {
                'test_id': test['id'],
                'test_type': 'needle',
                'model_used': self.model_name,
                'scores': {},
                'overall_score': 0.0,
                'reasoning': f"Grading failed: {e}",
                'error': str(e)
            }
    
    def grade_summary_test(self, test: Dict[str, Any], answer: str) -> Dict[str, Any]:
        """
        Grade a summary agent test using Gemini LLM judge.
        
        Evaluates: comprehensiveness, coherence, synthesis, relevance
        
        Args:
            test: Test case with question and ground truth
            answer: Agent's answer string
            
        Returns:
            dict: Grading results with scores and reasoning
        """
        question = test['question']
        ground_truth = test.get('ground_truth', '')
        
        prompt = f"""You are evaluating a summary generated by an AI agent. Your task is to COMPARE the agent's summary against a reference summary (Ground Truth) to assess semantic quality.

IMPORTANT: The agent's summary does NOT need to use the same exact words as the Ground Truth. What matters is whether it conveys the same key information and meaning. Different phrasing is acceptable as long as the content is semantically equivalent.

Question: {question}

Reference Summary (Ground Truth): {ground_truth}

Agent's Summary: {answer}

Compare these two summaries and evaluate the agent's summary on the following criteria (score each from 0.0 to 1.0):

1. **Comprehensiveness**: Does the agent's summary cover all major points from the reference?
   - 1.0: All major points covered thoroughly (even if worded differently)
   - 0.5: Some major points covered, some missing or incomplete
   - 0.0: Missing most major points

2. **Coherence**: Is the agent's summary well-organized and logically structured?
   - 1.0: Excellent organization and logical flow
   - 0.5: Somewhat organized but could be clearer
   - 0.0: Disorganized or confusing structure

3. **Synthesis**: Does the agent's summary integrate information effectively into a cohesive narrative?
   - 1.0: Excellent synthesis - information flows naturally as unified summary
   - 0.5: Some synthesis but feels like disconnected facts
   - 0.0: No synthesis, just isolated statements

4. **Relevance**: Does the agent's summary directly address the question without unnecessary information?
   - 1.0: Highly relevant, directly addresses question, no fluff
   - 0.5: Mostly relevant with some tangential information
   - 0.0: Not relevant or contains mostly irrelevant information

5. **Accuracy**: Are the facts in the agent's summary semantically correct compared to the reference?
   - 1.0: All facts semantically accurate (exact wording doesn't matter)
   - 0.5: Most facts accurate, some errors or omissions
   - 0.0: Many factual errors or hallucinations

Return ONLY a valid, complete JSON object with this exact structure (no markdown, no code blocks, keep reasoning under 50 words):
{{
  "comprehensiveness": <score 0.0-1.0>,
  "coherence": <score 0.0-1.0>,
  "synthesis": <score 0.0-1.0>,
  "relevance": <score 0.0-1.0>,
  "accuracy": <score 0.0-1.0>,
  "overall_score": <average of all scores>,
  "reasoning": "<brief 1-2 sentence explanation>"
}}"""
        
        try:
            # Call LLM (OpenAI or Gemini) using helper method
            try:
                response_text = self._call_llm(prompt)
            except ValueError as e:
                # Handle blocked responses (Gemini safety filters)
                if "blocked by safety filters" in str(e):
                    print(f"[WARNING] LLM blocked response for {test['id']} (safety filters)")
                    return {
                        'test_id': test['id'],
                        'test_type': 'summary',
                        'model_used': self.model_name,
                        'scores': {
                            'comprehensiveness': 0.0,
                            'coherence': 0.0,
                            'synthesis': 0.0,
                            'relevance': 0.0,
                            'accuracy': 0.0,
                            'overall_score': 0.0
                        },
                        'overall_score': 0.0,
                        'reasoning': 'Response blocked by safety filters',
                        'blocked': True
                    }
                else:
                    raise
            
            # Parse JSON response using helper method
            scores = self._parse_json_response(response_text, test['id'])
            
            # Build result
            result = {
                'test_id': test['id'],
                'test_type': 'summary',
                'model_used': self.model_name,
                'scores': scores,
                'overall_score': scores.get('overall_score', 0.0),
                'reasoning': scores.get('reasoning', ''),
                'criteria_evaluated': list(scores.keys())
            }
            
            return result
            
        except Exception as e:
            print(f"[ERROR] Model grading failed for {test['id']}: {e}")
            return {
                'test_id': test['id'],
                'test_type': 'summary',
                'model_used': self.model_name,
                'scores': {},
                'overall_score': 0.0,
                'reasoning': f"Grading failed: {e}",
                'error': str(e)
            }
    
    def grade_batch(self, tests: List[Dict[str, Any]], answers: Dict[str, Any], test_type: str, 
                   delay_between_calls: float = 1.0) -> Dict[str, Any]:
        """
        Grade multiple tests in batch with rate limiting.
        
        Args:
            tests: List of test cases
            answers: Dictionary mapping test_id to answer
            test_type: Type of test ('needle' or 'summary')
            delay_between_calls: Seconds to wait between API calls (rate limiting)
            
        Returns:
            dict: Batch grading results
        """
        results = {
            'test_type': test_type,
            'total_tests': len(tests),
            'average_score': 0.0,
            'individual_results': []
        }
        
        total_score = 0.0
        
        for i, test in enumerate(tests):
            test_id = test['id']
            
            print(f"[MODEL GRADER] Grading {test_id} ({i+1}/{len(tests)})...")
            
            if test_id not in answers:
                # Test not answered
                result = {
                    'test_id': test_id,
                    'test_type': test_type,
                    'overall_score': 0.0,
                    'reasoning': 'Test not answered'
                }
            else:
                # Grade based on test type
                answer = answers[test_id].get('answer', '')
                
                if test_type == 'needle':
                    result = self.grade_needle_test(test, answer)
                elif test_type == 'summary':
                    result = self.grade_summary_test(test, answer)
                else:
                    result = {
                        'test_id': test_id,
                        'test_type': test_type,
                        'overall_score': 0.0,
                        'reasoning': f'Unknown test type: {test_type}'
                    }
            
            results['individual_results'].append(result)
            total_score += result.get('overall_score', 0.0)
            
            # Rate limiting - wait between calls to avoid hitting API limits
            if i < len(tests) - 1:  # Don't wait after last call
                time.sleep(delay_between_calls)
        
        results['average_score'] = total_score / len(tests) if tests else 0.0
        
        return results


# Example usage and testing
if __name__ == "__main__":
    try:
        grader = ModelGrader()
        
        # Test needle grading
        test_needle = {
            "id": "needle_test",
            "question": "What time did the collision occur?",
            "ground_truth": "The collision occurred at 09:23:45 AM on January 15, 2024.",
            "model_grader_criteria": ["factual_accuracy", "completeness", "precision"]
        }
        
        answer_needle = "The collision happened at 09:23:45 AM on January 15, 2024."
        
        result = grader.grade_needle_test(test_needle, answer_needle)
        print("\nNeedle Test Result:")
        print(f"  Overall Score: {result['overall_score']:.2f}")
        print(f"  Reasoning: {result['reasoning']}")
        print(f"  Scores: {result['scores']}")
        
    except Exception as e:
        print(f"Error: {e}")
