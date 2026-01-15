"""
JSON Reporter for QA Testing Suite

Aggregates test results from all graders and saves to JSON format
for programmatic access and further analysis.
"""

import json
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime


class JSONReporter:
    """
    Generates JSON reports from QA test results.
    
    Aggregates:
    - Code grader results
    - Model grader results
    - Human-in-the-loop results
    - Overall statistics and scores
    """
    
    def __init__(self):
        """Initialize the JSON reporter."""
        pass
    
    def aggregate_results(self, 
                         needle_code_results: Dict[str, Any] = None,
                         needle_model_results: Dict[str, Any] = None,
                         summary_code_results: Dict[str, Any] = None,
                         summary_model_results: Dict[str, Any] = None,
                         routing_results: Dict[str, Any] = None,
                         hitl_results: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Aggregate results from all graders into a unified structure.
        
        Args:
            needle_code_results: Code grader results for needle tests
            needle_model_results: Model grader results for needle tests
            summary_code_results: Code grader results for summary tests
            summary_model_results: Model grader results for summary tests
            routing_results: Routing test results
            hitl_results: Human-in-the-loop results
            
        Returns:
            dict: Aggregated results with overall statistics
        """
        report = {
            'metadata': {
                'report_generated': datetime.now().isoformat(),
                'report_type': 'qa_testing_suite',
                'version': '1.0.0'
            },
            'overall_scores': {},
            'agent_scores': {
                'needle_agent': {},
                'summary_agent': {},
                'routing_agent': {}
            },
            'grader_scores': {
                'code_grader': {},
                'model_grader': {},
                'hitl_grader': {}
            },
            'detailed_results': {
                'needle_tests': [],
                'summary_tests': [],
                'routing_tests': [],
                'hitl_tests': []
            }
        }
        
        # Aggregate needle agent results
        if needle_code_results or needle_model_results:
            needle_agg = self._aggregate_test_type_results(
                needle_code_results, 
                needle_model_results,
                'needle'
            )
            report['agent_scores']['needle_agent'] = needle_agg['agent_score']
            report['detailed_results']['needle_tests'] = needle_agg['detailed_results']
        
        # Aggregate summary agent results
        if summary_code_results or summary_model_results:
            summary_agg = self._aggregate_test_type_results(
                summary_code_results,
                summary_model_results,
                'summary'
            )
            report['agent_scores']['summary_agent'] = summary_agg['agent_score']
            report['detailed_results']['summary_tests'] = summary_agg['detailed_results']
        
        # Aggregate routing results
        if routing_results:
            routing_agg = self._aggregate_routing_results(routing_results)
            report['agent_scores']['routing_agent'] = routing_agg
            # Store detailed routing test results with timestamps
            routing_individual = routing_results.get('individual_results', [])
            for test_result in routing_individual:
                if 'graded_at' not in test_result:
                    test_result['graded_at'] = datetime.now().isoformat()
            report['detailed_results']['routing_tests'] = routing_individual
        
        # Aggregate HITL results
        if hitl_results:
            hitl_agg = self._aggregate_hitl_results(hitl_results)
            report['grader_scores']['hitl_grader'] = hitl_agg
            # Store detailed HITL test results with timestamps
            hitl_individual = hitl_results.get('individual_results', [])
            for test_result in hitl_individual:
                if 'graded_at' not in test_result:
                    test_result['graded_at'] = datetime.now().isoformat()
            report['detailed_results']['hitl_tests'] = hitl_individual
        
        # Calculate grader-level scores
        report['grader_scores']['code_grader'] = self._calculate_code_grader_score(
            needle_code_results, summary_code_results
        )
        
        report['grader_scores']['model_grader'] = self._calculate_model_grader_score(
            needle_model_results, summary_model_results
        )
        
        # Calculate overall system score
        report['overall_scores'] = self._calculate_overall_scores(report)
        
        return report
    
    def _aggregate_test_type_results(self, code_results: Dict[str, Any], 
                                    model_results: Dict[str, Any],
                                    test_type: str) -> Dict[str, Any]:
        """Aggregate code and model results for a specific test type."""
        agg = {
            'test_type': test_type,
            'agent_score': {},
            'detailed_results': []
        }
        
        # Get individual results from both graders
        code_individual = code_results.get('individual_results', []) if code_results else []
        model_individual = model_results.get('individual_results', []) if model_results else []
        
        # Create a mapping of test_id to results
        code_map = {r['test_id']: r for r in code_individual}
        model_map = {r['test_id']: r for r in model_individual}
        
        # Combine results per test
        all_test_ids = set(code_map.keys()) | set(model_map.keys())
        
        for test_id in sorted(all_test_ids):
            combined = {
                'test_id': test_id,
                'test_type': test_type,
                'graded_at': datetime.now().isoformat(),  # Timestamp when this test was graded
                'code_grader': code_map.get(test_id, {}),
                'model_grader': model_map.get(test_id, {}),
                'combined_score': 0.0
            }
            
            # Calculate combined score (average of available graders)
            scores = []
            if test_id in code_map:
                scores.append(code_map[test_id].get('score', 0.0))
            if test_id in model_map:
                scores.append(model_map[test_id].get('overall_score', 0.0))
            
            combined['combined_score'] = sum(scores) / len(scores) if scores else 0.0
            agg['detailed_results'].append(combined)
        
        # Calculate agent-level scores
        agg['agent_score'] = {
            'total_tests': len(agg['detailed_results']),
            'average_code_score': code_results.get('average_score', 0.0) if code_results else None,
            'average_model_score': model_results.get('average_score', 0.0) if model_results else None,
            'average_combined_score': sum(r['combined_score'] for r in agg['detailed_results']) / len(agg['detailed_results']) if agg['detailed_results'] else 0.0
        }
        
        return agg
    
    def _aggregate_routing_results(self, routing_results: Dict[str, Any]) -> Dict[str, Any]:
        """Aggregate routing test results."""
        individual = routing_results.get('individual_results', [])
        
        return {
            'total_tests': len(individual),
            'correct_routes': sum(1 for r in individual if r.get('passed', False)),
            'accuracy': routing_results.get('average_score', 0.0),
            'needle_accuracy': sum(1 for r in individual if r.get('expected_route') == 'needle' and r.get('passed')) / max(1, sum(1 for r in individual if r.get('expected_route') == 'needle')),
            'summary_accuracy': sum(1 for r in individual if r.get('expected_route') == 'summary' and r.get('passed')) / max(1, sum(1 for r in individual if r.get('expected_route') == 'summary'))
        }
    
    def _aggregate_hitl_results(self, hitl_results: Dict[str, Any]) -> Dict[str, Any]:
        """Aggregate human-in-the-loop results by agent type."""
        individual_results = hitl_results.get('individual_results', [])
        
        # Separate by agent type
        needle_tests = [r for r in individual_results if r.get('query_type') == 'needle' and not r.get('skipped', False)]
        summary_tests = [r for r in individual_results if r.get('query_type') == 'summary' and not r.get('skipped', False)]
        routing_tests = [r for r in individual_results if r.get('query_type') == 'routing' and not r.get('skipped', False)]
        
        result = {
            'total_tests': hitl_results.get('total_tests', 0),
            'completed_tests': hitl_results.get('completed_tests', 0),
            'skipped_tests': hitl_results.get('skipped_tests', 0),
            'average_rating': hitl_results.get('average_rating', 0.0),
            'average_score': hitl_results.get('average_score', 0.0),
            'by_agent_type': {}
        }
        
        # Needle agent HITL
        if needle_tests:
            result['by_agent_type']['needle'] = {
                'total_tests': len(needle_tests),
                'average_rating': sum(t['rating'] for t in needle_tests) / len(needle_tests),
                'average_score': sum(t['score'] for t in needle_tests) / len(needle_tests)
            }
        
        # Summary agent HITL
        if summary_tests:
            result['by_agent_type']['summary'] = {
                'total_tests': len(summary_tests),
                'average_rating': sum(t['rating'] for t in summary_tests) / len(summary_tests),
                'average_score': sum(t['score'] for t in summary_tests) / len(summary_tests)
            }
        
        # Routing agent HITL
        if routing_tests:
            result['by_agent_type']['routing'] = {
                'total_tests': len(routing_tests),
                'average_rating': sum(t['rating'] for t in routing_tests) / len(routing_tests),
                'average_score': sum(t['score'] for t in routing_tests) / len(routing_tests)
            }
        
        return result
    
    def _calculate_code_grader_score(self, needle_results: Dict[str, Any], 
                                    summary_results: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate overall code grader performance."""
        scores = []
        
        if needle_results:
            scores.append(needle_results.get('average_score', 0.0))
        if summary_results:
            scores.append(summary_results.get('average_score', 0.0))
        
        return {
            'average_score': sum(scores) / len(scores) if scores else 0.0,
            'needle_score': needle_results.get('average_score', 0.0) if needle_results else None,
            'summary_score': summary_results.get('average_score', 0.0) if summary_results else None
        }
    
    def _calculate_model_grader_score(self, needle_results: Dict[str, Any],
                                     summary_results: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate overall model grader performance."""
        scores = []
        
        if needle_results:
            scores.append(needle_results.get('average_score', 0.0))
        if summary_results:
            scores.append(summary_results.get('average_score', 0.0))
        
        return {
            'average_score': sum(scores) / len(scores) if scores else 0.0,
            'needle_score': needle_results.get('average_score', 0.0) if needle_results else None,
            'summary_score': summary_results.get('average_score', 0.0) if summary_results else None
        }
    
    def _calculate_overall_scores(self, report: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate overall system scores."""
        overall = {
            'system_score': 0.0,
            'agent_performance': {},
            'grader_performance': {}
        }
        
        # Agent scores
        agent_scores = []
        for agent_name, agent_data in report['agent_scores'].items():
            if isinstance(agent_data, dict) and agent_data:
                score = agent_data.get('average_combined_score') or agent_data.get('accuracy', 0.0)
                overall['agent_performance'][agent_name] = score
                agent_scores.append(score)
        
        # Grader scores
        for grader_name, grader_data in report['grader_scores'].items():
            if isinstance(grader_data, dict) and grader_data:
                score = grader_data.get('average_score', 0.0)
                overall['grader_performance'][grader_name] = score
        
        # Overall system score (average of all agent scores)
        overall['system_score'] = sum(agent_scores) / len(agent_scores) if agent_scores else 0.0
        
        return overall
    
    def _merge_with_existing_results(self, new_report: Dict[str, Any], output_path: str) -> Dict[str, Any]:
        """
        Merge new test results with existing results in the file.
        
        This allows incremental testing - run needle tests, then summary tests,
        and have both in the final report.
        
        Args:
            new_report: New test results to add
            output_path: Path to existing results file
            
        Returns:
            dict: Merged results combining old and new
        """
        output_file = Path(output_path)
        
        # If no existing file, return new report as-is
        if not output_file.exists():
            return new_report
        
        # Load existing results
        try:
            with open(output_file, 'r', encoding='utf-8') as f:
                existing = json.load(f)
            print("[JSON REPORTER] Merging with existing results...")
        except (json.JSONDecodeError, IOError):
            # If file is corrupted or unreadable, use new report
            print("[JSON REPORTER] Could not load existing results, creating new file")
            return new_report
        
        # Merge agent scores (keep non-empty results from both)
        for agent in ['needle_agent', 'summary_agent', 'routing_agent']:
            existing_agent = existing.get('agent_scores', {}).get(agent, {})
            new_agent = new_report.get('agent_scores', {}).get(agent, {})
            
            # If new has data, use new; otherwise keep existing
            if new_agent:
                existing['agent_scores'][agent] = new_agent
        
        # Merge detailed test results
        for test_type in ['needle_tests', 'summary_tests', 'routing_tests', 'hitl_tests']:
            new_tests = new_report.get('detailed_results', {}).get(test_type, [])
            
            # If new has tests for this type, replace; otherwise keep existing
            if new_tests:
                existing['detailed_results'][test_type] = new_tests
        
        # Recalculate grader scores
        existing['grader_scores']['code_grader'] = self._calculate_code_grader_score_from_merged(existing)
        existing['grader_scores']['model_grader'] = self._calculate_model_grader_score_from_merged(existing)
        
        # Preserve or update HITL grader scores (must be done BEFORE calculating overall scores)
        new_hitl = new_report.get('grader_scores', {}).get('hitl_grader', {})
        if new_hitl:
            existing['grader_scores']['hitl_grader'] = new_hitl
        
        # Recalculate overall scores based on merged data (must be done AFTER updating all grader scores)
        existing['overall_scores'] = self._calculate_overall_scores(existing)
        
        # Update metadata timestamp
        existing['metadata']['report_generated'] = datetime.now().isoformat()
        
        # Report what was merged
        merged_agents = []
        for agent in ['needle_agent', 'summary_agent', 'routing_agent']:
            if existing.get('agent_scores', {}).get(agent):
                agent_name = agent.replace('_', ' ').title()
                merged_agents.append(agent_name)
        
        if merged_agents:
            print(f"[JSON REPORTER] Combined results include: {', '.join(merged_agents)}")
        
        return existing
    
    def _calculate_code_grader_score_from_merged(self, merged_results: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate code grader scores from merged results."""
        needle_tests = merged_results.get('detailed_results', {}).get('needle_tests', [])
        summary_tests = merged_results.get('detailed_results', {}).get('summary_tests', [])
        
        needle_scores = [t.get('code_grader', {}).get('score', 0) for t in needle_tests if t.get('code_grader')]
        summary_scores = [t.get('code_grader', {}).get('score', 0) for t in summary_tests if t.get('code_grader')]
        
        all_scores = needle_scores + summary_scores
        avg_score = sum(all_scores) / len(all_scores) if all_scores else 0.0
        
        return {
            'average_score': avg_score,
            'needle_score': sum(needle_scores) / len(needle_scores) if needle_scores else None,
            'summary_score': sum(summary_scores) / len(summary_scores) if summary_scores else None
        }
    
    def _calculate_model_grader_score_from_merged(self, merged_results: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate model grader scores from merged results."""
        needle_tests = merged_results.get('detailed_results', {}).get('needle_tests', [])
        summary_tests = merged_results.get('detailed_results', {}).get('summary_tests', [])
        
        needle_scores = [t.get('model_grader', {}).get('overall_score', 0) for t in needle_tests if t.get('model_grader')]
        summary_scores = [t.get('model_grader', {}).get('overall_score', 0) for t in summary_tests if t.get('model_grader')]
        
        all_scores = needle_scores + summary_scores
        avg_score = sum(all_scores) / len(all_scores) if all_scores else 0.0
        
        return {
            'average_score': avg_score,
            'needle_score': sum(needle_scores) / len(needle_scores) if needle_scores else None,
            'summary_score': sum(summary_scores) / len(summary_scores) if summary_scores else None
        }
    
    def save_report(self, report: Dict[str, Any], output_path: str, merge_with_existing: bool = True):
        """
        Save aggregated report to JSON file.
        
        Args:
            report: Aggregated report data
            output_path: Path to save JSON file
            merge_with_existing: If True, merge with existing results (default: True)
        """
        try:
            # Ensure directory exists
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            
            # Merge with existing results if requested
            if merge_with_existing:
                report = self._merge_with_existing_results(report, output_path)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            
            print(f"[JSON REPORTER] Report saved to {output_path}")
            
            # Print summary
            print("\n" + "=" * 70)
            print("QA TEST RESULTS SUMMARY")
            print("=" * 70)
            
            if 'overall_scores' in report:
                print(f"\nOverall System Score: {report['overall_scores']['system_score']:.3f}")
                
                print("\nAgent Performance:")
                for agent, score in report['overall_scores']['agent_performance'].items():
                    print(f"  {agent}: {score:.3f}")
                
                if report['overall_scores']['grader_performance']:
                    print("\nGrader Performance:")
                    for grader, score in report['overall_scores']['grader_performance'].items():
                        if score > 0:
                            print(f"  {grader}: {score:.3f}")
            
            print("=" * 70 + "\n")
            
        except Exception as e:
            print(f"[ERROR] Failed to save JSON report: {e}")
            raise
    
    def load_report(self, input_path: str) -> Dict[str, Any]:
        """
        Load a previously saved report.
        
        Args:
            input_path: Path to JSON file
            
        Returns:
            dict: Loaded report data
        """
        try:
            with open(input_path, 'r', encoding='utf-8') as f:
                report = json.load(f)
            
            print(f"[JSON REPORTER] Report loaded from {input_path}")
            return report
            
        except FileNotFoundError:
            print(f"[ERROR] File not found: {input_path}")
            return {}
        except Exception as e:
            print(f"[ERROR] Failed to load report: {e}")
            return {}


# Example usage
if __name__ == "__main__":
    reporter = JSONReporter()
    
    # Example aggregation
    example_results = {
        'needle_code_results': {
            'average_score': 0.85,
            'individual_results': [
                {'test_id': 'needle_01', 'score': 0.9}
            ]
        }
    }
    
    report = reporter.aggregate_results(**example_results)
    print(json.dumps(report, indent=2))
