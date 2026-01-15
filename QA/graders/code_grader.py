"""
Code-Based Grader for QA Testing Suite

Uses regex patterns and exact matching to validate factual correctness
of agent responses. Fast, deterministic, and cost-free.
"""

import re
from typing import Dict, List, Any


class CodeGrader:
    """
    Applies code-based grading using regex patterns and exact string matching.
    
    Used for:
    - Needle Agent: Validate specific facts (dates, times, numbers, names)
    - Summary Agent: Check presence of key facts and figures
    - Routing Agent: Exact route matching
    """
    
    def __init__(self):
        """Initialize the code grader."""
        pass
    
    def grade_needle_test(self, test: Dict[str, Any], answer: str) -> Dict[str, Any]:
        """
        Grade a needle agent test using regex patterns.
        
        Args:
            test: Test case with code_grader_checks
            answer: Agent's answer string
            
        Returns:
            dict: Grading results with individual check scores
        """
        checks = test.get('code_grader_checks', {})
        results = {
            'test_id': test['id'],
            'test_type': 'needle',
            'checks': {},
            'passed_checks': 0,
            'total_checks': len(checks),
            'score': 0.0,
            'details': []
        }
        
        if not checks:
            results['score'] = 1.0
            results['details'].append("No code grader checks defined")
            return results
        
        for check_name, pattern in checks.items():
            check_result = self._check_pattern(answer, pattern, check_name)
            results['checks'][check_name] = check_result
            
            if check_result['passed']:
                results['passed_checks'] += 1
                results['details'].append(f"[PASS] {check_name}: Found '{check_result['matched']}'")
            else:
                results['details'].append(f"[FAIL] {check_name}: Pattern '{pattern}' not found")
        
        # Calculate overall score
        results['score'] = results['passed_checks'] / results['total_checks'] if results['total_checks'] > 0 else 0.0
        
        return results
    
    def grade_summary_test(self, test: Dict[str, Any], answer: str) -> Dict[str, Any]:
        """
        Grade a summary agent test using regex patterns.
        
        For summaries, we check for presence of key facts/figures.
        
        Args:
            test: Test case with code_grader_checks
            answer: Agent's answer string
            
        Returns:
            dict: Grading results with individual check scores
        """
        checks = test.get('code_grader_checks', {})
        results = {
            'test_id': test['id'],
            'test_type': 'summary',
            'checks': {},
            'passed_checks': 0,
            'total_checks': len(checks),
            'score': 0.0,
            'details': []
        }
        
        if not checks:
            results['score'] = 1.0
            results['details'].append("No code grader checks defined")
            return results
        
        for check_name, pattern in checks.items():
            check_result = self._check_pattern(answer, pattern, check_name)
            results['checks'][check_name] = check_result
            
            if check_result['passed']:
                results['passed_checks'] += 1
                results['details'].append(f"[PASS] {check_name}: Found '{check_result['matched']}'")
            else:
                results['details'].append(f"[FAIL] {check_name}: Pattern '{pattern}' not found")
        
        # Calculate overall score
        results['score'] = results['passed_checks'] / results['total_checks'] if results['total_checks'] > 0 else 0.0
        
        return results
    
    def grade_routing_test(self, test: Dict[str, Any], actual_route: str) -> Dict[str, Any]:
        """
        Grade a routing agent test by comparing expected vs actual route.
        
        Args:
            test: Test case with expected_route
            actual_route: Actual route chosen by routing agent ('needle' or 'summary')
            
        Returns:
            dict: Grading results with pass/fail
        """
        expected_route = test.get('expected_route', '').lower()
        actual_route = actual_route.lower()
        
        passed = expected_route == actual_route
        
        results = {
            'test_id': test['id'],
            'test_type': 'routing',
            'expected_route': expected_route,
            'actual_route': actual_route,
            'passed': passed,
            'score': 1.0 if passed else 0.0,
            'details': []
        }
        
        if passed:
            results['details'].append(f"[PASS] Correct routing: {actual_route}")
        else:
            results['details'].append(f"[FAIL] Incorrect routing: expected '{expected_route}', got '{actual_route}'")
        
        return results
    
    def _check_pattern(self, text: str, pattern: str, check_name: str) -> Dict[str, Any]:
        """
        Check if a regex pattern exists in the text.
        
        Args:
            text: Text to search in
            pattern: Regex pattern to search for
            check_name: Name of the check (for logging)
            
        Returns:
            dict: Check result with passed status and matched text
        """
        try:
            # Case-insensitive search by default
            match = re.search(pattern, text, re.IGNORECASE)
            
            if match:
                return {
                    'passed': True,
                    'matched': match.group(0),
                    'pattern': pattern,
                    'check_name': check_name
                }
            else:
                return {
                    'passed': False,
                    'matched': None,
                    'pattern': pattern,
                    'check_name': check_name
                }
        except re.error as e:
            return {
                'passed': False,
                'matched': None,
                'pattern': pattern,
                'check_name': check_name,
                'error': f"Invalid regex: {e}"
            }
    
    def grade_batch(self, tests: List[Dict[str, Any]], answers: Dict[str, Any], test_type: str) -> Dict[str, Any]:
        """
        Grade multiple tests in batch.
        
        Args:
            tests: List of test cases
            answers: Dictionary mapping test_id to answer/route
            test_type: Type of test ('needle', 'summary', 'routing')
            
        Returns:
            dict: Batch grading results
        """
        results = {
            'test_type': test_type,
            'total_tests': len(tests),
            'passed_tests': 0,
            'average_score': 0.0,
            'individual_results': []
        }
        
        total_score = 0.0
        
        for test in tests:
            test_id = test['id']
            
            if test_id not in answers:
                # Test not answered
                result = {
                    'test_id': test_id,
                    'test_type': test_type,
                    'score': 0.0,
                    'details': ['Test not answered']
                }
            else:
                # Grade based on test type
                if test_type == 'needle':
                    answer = answers[test_id].get('answer', '')
                    result = self.grade_needle_test(test, answer)
                elif test_type == 'summary':
                    answer = answers[test_id].get('answer', '')
                    result = self.grade_summary_test(test, answer)
                elif test_type == 'routing':
                    actual_route = answers[test_id].get('route', '')
                    result = self.grade_routing_test(test, actual_route)
                else:
                    result = {
                        'test_id': test_id,
                        'test_type': test_type,
                        'score': 0.0,
                        'details': [f'Unknown test type: {test_type}']
                    }
            
            results['individual_results'].append(result)
            total_score += result['score']
            
            if result['score'] >= 0.7:  # 70% threshold for "passed"
                results['passed_tests'] += 1
        
        results['average_score'] = total_score / len(tests) if tests else 0.0
        
        return results


# Example usage and testing
if __name__ == "__main__":
    grader = CodeGrader()
    
    # Test needle grading
    test_needle = {
        "id": "needle_01",
        "question": "What time did the collision occur?",
        "code_grader_checks": {
            "time_pattern": "09:23:45|09:23",
            "time_format": "\\d{2}:\\d{2}(:\\d{2})?\\s*(AM|PM)",
            "date_pattern": "January 15, 2024|2024-01-15"
        }
    }
    
    answer_needle = "The collision occurred at 09:23:45 AM on January 15, 2024."
    
    result = grader.grade_needle_test(test_needle, answer_needle)
    print("Needle Test Result:")
    print(f"  Score: {result['score']:.2f}")
    print(f"  Passed: {result['passed_checks']}/{result['total_checks']}")
    for detail in result['details']:
        print(f"  {detail}")
    
    # Test routing grading
    test_routing = {
        "id": "routing_01",
        "question": "What time did the collision occur?",
        "expected_route": "needle"
    }
    
    result = grader.grade_routing_test(test_routing, "needle")
    print("\nRouting Test Result:")
    print(f"  Score: {result['score']:.2f}")
    print(f"  {result['details'][0]}")
