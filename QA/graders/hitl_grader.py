"""
Human-in-the-Loop Grader for QA Testing Suite

Provides interactive CLI interface for human reviewers to rate
agent answers and provide qualitative feedback.
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent))


class HITLGrader:
    """
    Interactive human-in-the-loop grading interface.
    
    Allows human reviewers to:
    - View questions and agent answers
    - Rate answers on a 1-5 scale
    - Provide text feedback
    - Skip and come back later
    """
    
    def __init__(self):
        """Initialize the HITL grader."""
        self.reviewer = "user"  # Can be customized
    
    def grade_single_test(self, test: Dict[str, Any], answer: str, test_number: int = 1, total_tests: int = 1) -> Dict[str, Any]:
        """
        Grade a single test interactively with human reviewer.
        
        Args:
            test: Test case with question and evaluation criteria
            answer: Agent's answer string (or routing decision for routing tests)
            test_number: Current test number (for display)
            total_tests: Total number of tests (for display)
            
        Returns:
            dict: Human grading result with rating and feedback
        """
        test_id = test['id']
        question = test['question']
        query_type = test.get('query_type', 'unknown')
        criteria = test.get('evaluation_criteria', [])
        evaluation_type = test.get('evaluation_type', 'rating')  # 'rating' or 'binary'
        expected_route = test.get('expected_route', None)
        
        # Display test information
        print("\n" + "=" * 80)
        print(f"HUMAN-IN-THE-LOOP EVALUATION ({test_number}/{total_tests})")
        print("=" * 80)
        print(f"\nTest ID: {test_id}")
        print(f"Type: {query_type.upper()}")
        
        # For routing tests, show different information
        if evaluation_type == 'binary' and query_type == 'routing':
            print(f"\nQuestion:")
            print(f"  {question}")
            print(f"\nRouting Agent Decision: {answer.upper() if answer else 'N/A'}")
            print("\n" + "=" * 80)
            
            # Binary evaluation for routing
            while True:
                binary_input = input("\nWas the routing decision CORRECT? (y/n, or 's' to skip): ").strip().lower()
                
                if binary_input == 's':
                    print("[SKIPPED] Moving to next test...")
                    return {
                        'test_id': test_id,
                        'query_type': query_type,
                        'skipped': True,
                        'rating': None,
                        'feedback': '',
                        'reviewer': self.reviewer,
                        'timestamp': datetime.now().isoformat()
                    }
                elif binary_input in ['y', 'yes']:
                    rating = 5
                    normalized_score = 1.0
                    break
                elif binary_input in ['n', 'no']:
                    rating = 1
                    normalized_score = 0.0
                    break
                else:
                    print("[ERROR] Please enter 'y' for yes, 'n' for no, or 's' to skip.")
            
            result = {
                'test_id': test_id,
                'query_type': query_type,
                'skipped': False,
                'rating': rating,
                'score': normalized_score,
                'feedback': '',
                'reviewer': self.reviewer,
                'timestamp': datetime.now().isoformat(),
                'criteria': criteria,
                'evaluation_type': 'binary',
                'expected_route': expected_route,
                'actual_route': answer
            }
            
            print(f"\n[SAVED] Saved! Routing {'CORRECT' if normalized_score == 1.0 else 'INCORRECT'} (Score: {normalized_score:.2f})")
            
        else:
            # Standard rating evaluation (for needle/summary tests)
            print(f"\nQuestion:")
            print(f"  {question}")
            print(f"\nAgent's Answer:")
            print(f"  {answer}")
            print(f"\nEvaluation Criteria:")
            for i, criterion in enumerate(criteria, 1):
                print(f"  {i}. {criterion}")
            print("\n" + "=" * 80)
            
            # Collect rating
            while True:
                try:
                    rating_input = input("\nRate this answer (1=Poor, 2=Fair, 3=Good, 4=Very Good, 5=Excellent, or 's' to skip): ").strip().lower()
                    
                    if rating_input == 's':
                        print("[SKIPPED] Moving to next test...")
                        return {
                            'test_id': test_id,
                            'query_type': query_type,
                            'skipped': True,
                            'rating': None,
                            'feedback': '',
                            'reviewer': self.reviewer,
                            'timestamp': datetime.now().isoformat()
                        }
                    
                    rating = int(rating_input)
                    if 1 <= rating <= 5:
                        break
                    else:
                        print("[ERROR] Please enter a number between 1 and 5, or 's' to skip.")
                except ValueError:
                    print("[ERROR] Invalid input. Please enter a number between 1 and 5, or 's' to skip.")
            
            # Collect feedback (optional)
            feedback = input("Feedback (optional, press Enter to skip): ").strip()
            
            # Normalize rating to 0.0-1.0 scale
            normalized_score = (rating - 1) / 4.0  # 1->0.0, 2->0.25, 3->0.5, 4->0.75, 5->1.0
            
            result = {
                'test_id': test_id,
                'query_type': query_type,
                'skipped': False,
                'rating': rating,
                'score': normalized_score,
                'feedback': feedback,
                'reviewer': self.reviewer,
                'timestamp': datetime.now().isoformat(),
                'criteria': criteria
            }
            
            print(f"\n[SAVED] Saved! Rating: {rating}/5 (Score: {normalized_score:.2f})")
        
        return result
    
    def grade_batch(self, tests: List[Dict[str, Any]], answers: Dict[str, Any]) -> Dict[str, Any]:
        """
        Grade multiple tests in batch with interactive review.
        
        Args:
            tests: List of test cases
            answers: Dictionary mapping test_id to answer
            
        Returns:
            dict: Batch grading results with all human ratings
        """
        results = {
            'test_type': 'hitl',
            'total_tests': len(tests),
            'completed_tests': 0,
            'skipped_tests': 0,
            'average_score': 0.0,
            'average_rating': 0.0,
            'individual_results': [],
            'session_start': datetime.now().isoformat()
        }
        
        print("\n" + "=" * 80)
        print("HUMAN-IN-THE-LOOP EVALUATION SESSION")
        print("=" * 80)
        print(f"\nTotal tests to review: {len(tests)}")
        print("You can skip tests by entering 's' when asked for a rating.")
        print("\nPress Ctrl+C at any time to save progress and exit.")
        print("=" * 80)
        
        total_score = 0.0
        total_rating = 0.0
        
        try:
            for i, test in enumerate(tests):
                test_id = test['id']
                
                if test_id not in answers:
                    # Test not answered by agent
                    print(f"\n[WARNING] Test {test_id} has no agent answer. Skipping...")
                    result = {
                        'test_id': test_id,
                        'test_type': test.get('query_type', 'unknown'),
                        'skipped': True,
                        'rating': None,
                        'feedback': 'No agent answer available',
                        'reviewer': self.reviewer,
                        'timestamp': datetime.now().isoformat()
                    }
                    results['skipped_tests'] += 1
                else:
                    # Get answer and grade
                    answer = answers[test_id].get('answer', '')
                    result = self.grade_single_test(test, answer, i + 1, len(tests))
                    
                    if result['skipped']:
                        results['skipped_tests'] += 1
                    else:
                        results['completed_tests'] += 1
                        total_score += result['score']
                        total_rating += result['rating']
                
                results['individual_results'].append(result)
                
                # Offer to save progress
                if (i + 1) % 5 == 0 and i < len(tests) - 1:
                    save_progress = input("\n[CHECKPOINT] Save progress? (Y/n): ").strip().lower()
                    if save_progress != 'n':
                        print("[INFO] Progress saved to results.")
        
        except KeyboardInterrupt:
            print("\n\n[INTERRUPTED] Saving progress...")
        
        # Calculate averages
        if results['completed_tests'] > 0:
            results['average_score'] = total_score / results['completed_tests']
            results['average_rating'] = total_rating / results['completed_tests']
        
        results['session_end'] = datetime.now().isoformat()
        
        # Display summary
        print("\n" + "=" * 80)
        print("EVALUATION SESSION COMPLETE")
        print("=" * 80)
        print(f"Completed: {results['completed_tests']}/{results['total_tests']}")
        print(f"Skipped: {results['skipped_tests']}")
        if results['completed_tests'] > 0:
            print(f"Average Rating: {results['average_rating']:.2f}/5")
            print(f"Average Score: {results['average_score']:.2f}")
        print("=" * 80)
        
        return results
    
    def resume_session(self, tests: List[Dict[str, Any]], answers: Dict[str, Any], 
                      previous_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Resume a previous HITL session, only grading tests that were skipped.
        
        Args:
            tests: List of test cases
            answers: Dictionary mapping test_id to answer
            previous_results: Previous HITL results to resume from
            
        Returns:
            dict: Updated batch grading results
        """
        # Find tests that were skipped or not completed
        completed_test_ids = {
            r['test_id'] for r in previous_results.get('individual_results', [])
            if not r.get('skipped', False)
        }
        
        remaining_tests = [t for t in tests if t['id'] not in completed_test_ids]
        
        if not remaining_tests:
            print("[INFO] All tests have been completed. Nothing to resume.")
            return previous_results
        
        print(f"\n[RESUME] Found {len(remaining_tests)} tests to complete.")
        
        # Grade remaining tests
        new_results = self.grade_batch(remaining_tests, answers)
        
        # Merge results
        merged_results = {
            'test_type': 'hitl',
            'total_tests': len(tests),
            'completed_tests': previous_results.get('completed_tests', 0) + new_results['completed_tests'],
            'skipped_tests': new_results['skipped_tests'],
            'individual_results': previous_results.get('individual_results', []) + new_results['individual_results'],
            'session_start': previous_results.get('session_start', datetime.now().isoformat()),
            'session_end': datetime.now().isoformat()
        }
        
        # Recalculate averages
        total_score = sum(r['score'] for r in merged_results['individual_results'] if not r.get('skipped', False))
        total_rating = sum(r['rating'] for r in merged_results['individual_results'] if not r.get('skipped', False))
        
        if merged_results['completed_tests'] > 0:
            merged_results['average_score'] = total_score / merged_results['completed_tests']
            merged_results['average_rating'] = total_rating / merged_results['completed_tests']
        else:
            merged_results['average_score'] = 0.0
            merged_results['average_rating'] = 0.0
        
        return merged_results


# Example usage and testing
if __name__ == "__main__":
    grader = HITLGrader()
    
    # Example test
    test_example = {
        "id": "hitl_needle_01",
        "question": "What injuries did Sarah Mitchell sustain?",
        "query_type": "needle",
        "evaluation_criteria": [
            "Completeness: Are all injuries mentioned?",
            "Clarity: Is the answer easy to understand?",
            "Medical accuracy: Are medical terms used correctly?"
        ]
    }
    
    answer_example = "Sarah Mitchell sustained Grade 2 whiplash injury, cervical spine strain, and a mild concussion."
    
    print("Example HITL Grading Session")
    result = grader.grade_single_test(test_example, answer_example, 1, 1)
    
    print("\nResult:")
    print(json.dumps(result, indent=2))
