"""
Answer Collector for QA Testing Suite

Runs agents on test questions and caches responses for efficient grading.
Allows graders to be run multiple times without re-querying agents.
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime
import time

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent))

from Agents.routing_agent import RoutingAgent
from Agents.needle_agent import NeedleAgent
from Agents.summary_agent import SummaryAgent


class AnswerCollector:
    """
    Collects agent responses for QA tests and caches them.
    
    This allows:
    - Running expensive agents once
    - Iterating on graders without re-querying
    - Consistent baseline for grader comparisons
    """
    
    def __init__(self):
        """Initialize the answer collector with all agents."""
        print("[ANSWER COLLECTOR] Initializing agents...")
        
        try:
            self.routing_agent = RoutingAgent()
            print("[ANSWER COLLECTOR] - Routing agent ready")
            
            self.needle_agent = NeedleAgent()
            print("[ANSWER COLLECTOR] - Needle agent ready")
            
            self.summary_agent = SummaryAgent()
            print("[ANSWER COLLECTOR] - Summary agent ready")
            
            print("[ANSWER COLLECTOR] All agents initialized!\n")
        except Exception as e:
            print(f"[ERROR] Failed to initialize agents: {e}")
            raise
    
    def collect_needle_answers(self, tests: List[Dict[str, Any]], verbose: bool = True) -> Dict[str, Any]:
        """
        Collect needle agent answers for a list of tests.
        
        Args:
            tests: List of needle test cases
            verbose: Whether to print progress
            
        Returns:
            dict: Mapping of test_id to answer data
        """
        answers = {}
        
        if verbose:
            print(f"\n[ANSWER COLLECTOR] Collecting {len(tests)} needle agent answers...")
            print("=" * 70)
        
        for i, test in enumerate(tests):
            test_id = test['id']
            question = test['question']
            
            if verbose:
                print(f"\n[{i+1}/{len(tests)}] {test_id}")
                print(f"Question: {question}")
            
            try:
                start_time = time.time()
                
                # Get route first
                route = self.routing_agent.route(question)
                
                # Run needle agent
                result = self.needle_agent.answer_query(question)
                
                elapsed_time = time.time() - start_time
                
                # Store answer data
                answers[test_id] = {
                    'test_id': test_id,
                    'question': question,
                    'route': route,
                    'answer': result['answer'],
                    'sources': result['sources'],
                    'chunks_used': result.get('chunks_used', 0),
                    'parent_pages_used': result.get('parent_pages_used', 0),
                    'execution_time': elapsed_time,
                    'timestamp': datetime.now().isoformat(),
                    'agent_type': 'needle'
                }
                
                if verbose:
                    print(f"Answer: {result['answer'][:150]}...")
                    print(f"Time: {elapsed_time:.2f}s | Route: {route}")
                
            except Exception as e:
                print(f"[ERROR] Failed to collect answer for {test_id}: {e}")
                answers[test_id] = {
                    'test_id': test_id,
                    'question': question,
                    'error': str(e),
                    'timestamp': datetime.now().isoformat()
                }
        
        if verbose:
            print("\n" + "=" * 70)
            print(f"[ANSWER COLLECTOR] Collected {len(answers)} needle answers\n")
        
        return answers
    
    def collect_summary_answers(self, tests: List[Dict[str, Any]], verbose: bool = True) -> Dict[str, Any]:
        """
        Collect summary agent answers for a list of tests.
        
        Args:
            tests: List of summary test cases
            verbose: Whether to print progress
            
        Returns:
            dict: Mapping of test_id to answer data
        """
        answers = {}
        
        if verbose:
            print(f"\n[ANSWER COLLECTOR] Collecting {len(tests)} summary agent answers...")
            print("=" * 70)
        
        for i, test in enumerate(tests):
            test_id = test['id']
            question = test['question']
            
            if verbose:
                print(f"\n[{i+1}/{len(tests)}] {test_id}")
                print(f"Question: {question}")
            
            try:
                start_time = time.time()
                
                # Get route first
                route = self.routing_agent.route(question)
                
                # Run summary agent
                result = self.summary_agent.answer_query(question)
                
                elapsed_time = time.time() - start_time
                
                # Store answer data
                answers[test_id] = {
                    'test_id': test_id,
                    'question': question,
                    'route': route,
                    'answer': result['answer'],
                    'sources': result['sources'],
                    'summaries_used': result.get('summaries_used', 0),
                    'execution_time': elapsed_time,
                    'timestamp': datetime.now().isoformat(),
                    'agent_type': 'summary'
                }
                
                if verbose:
                    print(f"Answer: {result['answer'][:150]}...")
                    print(f"Time: {elapsed_time:.2f}s | Route: {route}")
                
            except Exception as e:
                print(f"[ERROR] Failed to collect answer for {test_id}: {e}")
                answers[test_id] = {
                    'test_id': test_id,
                    'question': question,
                    'error': str(e),
                    'timestamp': datetime.now().isoformat()
                }
        
        if verbose:
            print("\n" + "=" * 70)
            print(f"[ANSWER COLLECTOR] Collected {len(answers)} summary answers\n")
        
        return answers
    
    def collect_routing_answers(self, tests: List[Dict[str, Any]], verbose: bool = True) -> Dict[str, Any]:
        """
        Collect routing decisions for a list of tests.
        
        Args:
            tests: List of routing test cases
            verbose: Whether to print progress
            
        Returns:
            dict: Mapping of test_id to routing data
        """
        answers = {}
        
        if verbose:
            print(f"\n[ANSWER COLLECTOR] Collecting {len(tests)} routing decisions...")
            print("=" * 70)
        
        for i, test in enumerate(tests):
            test_id = test['id']
            question = test['question']
            expected_route = test.get('expected_route', 'unknown')
            
            if verbose:
                print(f"\n[{i+1}/{len(tests)}] {test_id}")
                print(f"Question: {question}")
                print(f"Expected: {expected_route}")
            
            try:
                start_time = time.time()
                
                # Get routing decision
                route = self.routing_agent.route(question)
                
                elapsed_time = time.time() - start_time
                
                # Store routing data
                answers[test_id] = {
                    'test_id': test_id,
                    'question': question,
                    'route': route,
                    'expected_route': expected_route,
                    'correct': route.lower() == expected_route.lower(),
                    'execution_time': elapsed_time,
                    'timestamp': datetime.now().isoformat(),
                    'agent_type': 'routing'
                }
                
                status = "[PASS]" if answers[test_id]['correct'] else "[FAIL]"
                if verbose:
                    print(f"{status} Routed to: {route}")
                
            except Exception as e:
                print(f"[ERROR] Failed to get routing for {test_id}: {e}")
                answers[test_id] = {
                    'test_id': test_id,
                    'question': question,
                    'error': str(e),
                    'timestamp': datetime.now().isoformat()
                }
        
        if verbose:
            correct_count = sum(1 for a in answers.values() if a.get('correct', False))
            print("\n" + "=" * 70)
            print(f"[ANSWER COLLECTOR] Routing accuracy: {correct_count}/{len(answers)} ({100*correct_count/len(answers):.1f}%)\n")
        
        return answers
    
    def collect_all_answers(self, needle_tests: List[Dict[str, Any]], 
                           summary_tests: List[Dict[str, Any]],
                           routing_tests: List[Dict[str, Any]],
                           verbose: bool = True) -> Dict[str, Any]:
        """
        Collect answers for all test types.
        
        Args:
            needle_tests: Needle test cases
            summary_tests: Summary test cases
            routing_tests: Routing test cases
            verbose: Whether to print progress
            
        Returns:
            dict: All collected answers organized by test type
        """
        all_answers = {
            'metadata': {
                'collection_start': datetime.now().isoformat(),
                'total_tests': len(needle_tests) + len(summary_tests) + len(routing_tests)
            },
            'needle_answers': {},
            'summary_answers': {},
            'routing_answers': {}
        }
        
        # Collect needle answers
        if needle_tests:
            all_answers['needle_answers'] = self.collect_needle_answers(needle_tests, verbose)
        
        # Collect summary answers
        if summary_tests:
            all_answers['summary_answers'] = self.collect_summary_answers(summary_tests, verbose)
        
        # Collect routing answers
        if routing_tests:
            all_answers['routing_answers'] = self.collect_routing_answers(routing_tests, verbose)
        
        all_answers['metadata']['collection_end'] = datetime.now().isoformat()
        
        return all_answers
    
    def save_answers(self, answers: Dict[str, Any], output_path: str):
        """
        Save collected answers to JSON file.
        
        Args:
            answers: Collected answers data
            output_path: Path to save JSON file
        """
        try:
            # Ensure directory exists
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(answers, f, indent=2, ensure_ascii=False)
            
            print(f"[ANSWER COLLECTOR] Saved answers to {output_path}")
            
        except Exception as e:
            print(f"[ERROR] Failed to save answers: {e}")
            raise
    
    def load_answers(self, input_path: str) -> Dict[str, Any]:
        """
        Load previously collected answers from JSON file.
        
        Args:
            input_path: Path to JSON file
            
        Returns:
            dict: Loaded answers data
        """
        try:
            with open(input_path, 'r', encoding='utf-8') as f:
                answers = json.load(f)
            
            print(f"[ANSWER COLLECTOR] Loaded answers from {input_path}")
            return answers
            
        except FileNotFoundError:
            print(f"[ERROR] File not found: {input_path}")
            return {}
        except Exception as e:
            print(f"[ERROR] Failed to load answers: {e}")
            return {}


# Example usage
if __name__ == "__main__":
    collector = AnswerCollector()
    
    # Example test
    test_example = [
        {
            "id": "needle_01",
            "question": "What time did the collision occur?"
        }
    ]
    
    answers = collector.collect_needle_answers(test_example, verbose=True)
    
    print("\nCollected Answers:")
    print(json.dumps(answers, indent=2))
