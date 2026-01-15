"""
Human-in-the-Loop Test Runner

Interactive CLI for human reviewers to evaluate agent responses.
"""

import json
import sys
import argparse
from pathlib import Path
from datetime import datetime

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from Config import config
from QA.collectors.answer_collector import AnswerCollector
from QA.graders.hitl_grader import HITLGrader
from QA.reporters.json_reporter import JSONReporter
from QA.reporters.pdf_reporter import PDFReporter


def load_test_dataset(test_file: str) -> list:
    """Load test dataset from JSON file."""
    try:
        with open(test_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        tests = data.get('tests', [])
        print(f"[INFO] Loaded {len(tests)} tests from {test_file}")
        return tests
    
    except FileNotFoundError:
        print(f"[ERROR] Test file not found: {test_file}")
        return []
    except Exception as e:
        print(f"[ERROR] Failed to load test file: {e}")
        return []


def load_cached_answers(cache_file: str) -> dict:
    """Load cached answers if available."""
    try:
        with open(cache_file, 'r', encoding='utf-8') as f:
            cached = json.load(f)
        print(f"[INFO] Loaded cached answers from {cache_file}")
        return cached
    except FileNotFoundError:
        print(f"[INFO] No cached answers found. Will collect fresh answers.")
        return {}
    except Exception as e:
        print(f"[ERROR] Failed to load cached answers: {e}")
        return {}




def run_hitl_tests(test_type: str = 'all'):
    """Run human-in-the-loop tests."""
    print("\n" + "=" * 70)
    print("HUMAN-IN-THE-LOOP EVALUATION")
    print("=" * 70)
    
    # Load HITL tests
    hitl_tests = load_test_dataset(config.QA_HITL_TESTS)
    if not hitl_tests:
        print("[ERROR] No HITL tests found")
        return
    
    # Filter tests by type if specified
    if test_type == 'needle':
        tests_to_run = [t for t in hitl_tests if t.get('query_type') == 'needle']
        print(f"[INFO] Running {len(tests_to_run)} needle HITL tests")
    elif test_type == 'summary':
        tests_to_run = [t for t in hitl_tests if t.get('query_type') == 'summary']
        print(f"[INFO] Running {len(tests_to_run)} summary HITL tests")
    elif test_type == 'routing':
        tests_to_run = [t for t in hitl_tests if t.get('query_type') == 'routing']
        print(f"[INFO] Running {len(tests_to_run)} routing HITL tests")
    else:
        tests_to_run = hitl_tests
        print(f"[INFO] Running all {len(tests_to_run)} HITL tests")
    
    if not tests_to_run:
        print("[ERROR] No tests match the specified type")
        return
    
    # Load cached answers
    cache_file = config.QA_CACHED_ANSWERS
    cached_data = load_cached_answers(cache_file)
    
    # Collect answers if needed
    answers_dict = {}
    
    for test in tests_to_run:
        test_id = test['id']
        query_type = test.get('query_type', 'unknown')
        
        # For routing tests, we need the routing decision, not the full answer
        if query_type == 'routing':
            # Check routing cache
            cache_key = 'routing_answers'
            cached_route = None
            
            if cache_key in cached_data and test_id in cached_data[cache_key]:
                routing_data = cached_data[cache_key][test_id]
                cached_route = routing_data.get('route') or routing_data.get('answer')
                
            # Only use cache if we have a valid route (not 'unknown' or None)
            if cached_route and cached_route != 'unknown':
                answers_dict[test_id] = {
                    'answer': cached_route,
                    'agent_type': 'routing'
                }
            else:
                # Collect routing decision
                print(f"\n[INFO] Collecting routing decision for {test_id}...")
                collector = AnswerCollector()
                result = collector.collect_routing_answers([test], verbose=True)
                if test_id in result:
                    # Check for errors
                    if 'error' in result[test_id]:
                        print(f"[ERROR] Failed to route {test_id}: {result[test_id]['error']}")
                        answers_dict[test_id] = {
                            'answer': 'unknown',
                            'agent_type': 'routing'
                        }
                    else:
                        answers_dict[test_id] = {
                            'answer': result[test_id].get('route', 'unknown'),
                            'agent_type': 'routing'
                        }
        else:
            # Check cache first for needle/summary
            cache_key = f"{query_type}_answers"
            if cache_key in cached_data and test_id in cached_data[cache_key]:
                answers_dict[test_id] = cached_data[cache_key][test_id]
            else:
                # Need to collect this answer
                print(f"\n[INFO] Collecting answer for {test_id}...")
                
                if query_type == 'needle':
                    collector = AnswerCollector()
                    result = collector.collect_needle_answers([test], verbose=False)
                    answers_dict.update(result)
                elif query_type == 'summary':
                    collector = AnswerCollector()
                    result = collector.collect_summary_answers([test], verbose=False)
                    answers_dict.update(result)
    
    # Save collected answers to cache if any were collected
    if answers_dict:
        # Load existing cache to merge
        existing_cache = load_cached_answers(cache_file)
        
        # Update cache with collected answers
        for test_id, answer_data in answers_dict.items():
            query_type = answer_data.get('agent_type', 'unknown')
            cache_key = f"{query_type}_answers"
            
            if cache_key not in existing_cache:
                existing_cache[cache_key] = {}
            
            # Add timestamp when cached
            answer_data['cached_at'] = datetime.now().isoformat()
            existing_cache[cache_key][test_id] = answer_data
        
        # Update metadata
        existing_cache['_metadata'] = {
            "last_updated": datetime.now().isoformat(),
            "version": "1.0.0",
            "description": "Cached answers from QA test runs"
        }
        
        # Save updated cache
        try:
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(existing_cache, f, indent=2, ensure_ascii=False)
            print(f"[INFO] Saved {len(answers_dict)} answers to cache")
        except Exception as e:
            print(f"[WARNING] Could not save answers to cache: {e}")
    
    # Run HITL grader
    grader = HITLGrader()
    
    # Check for existing HITL results in main QA results to resume
    try:
        with open(config.QA_RESULTS_JSON, 'r') as f:
            qa_results = json.load(f)
        
        # Extract HITL tests from existing results
        existing_hitl = qa_results.get('detailed_results', {}).get('hitl_tests', [])
        
        if existing_hitl:
            # Reconstruct previous_results format for resume
            previous_results = {
                'test_type': 'hitl',
                'total_tests': len(existing_hitl),
                'completed_tests': sum(1 for t in existing_hitl if not t.get('skipped', False)),
                'skipped_tests': sum(1 for t in existing_hitl if t.get('skipped', False)),
                'individual_results': existing_hitl
            }
            
            resume = input("\n[INFO] Found previous HITL results. Resume? (Y/n): ").strip().lower()
            if resume != 'n':
                results = grader.resume_session(tests_to_run, answers_dict, previous_results)
            else:
                results = grader.grade_batch(tests_to_run, answers_dict)
        else:
            results = grader.grade_batch(tests_to_run, answers_dict)
    except FileNotFoundError:
        print("[INFO] No existing QA results found. Starting fresh HITL evaluation.")
        results = grader.grade_batch(tests_to_run, answers_dict)
    
    # Always merge HITL results into main QA results
    try:
        print("\n[INFO] Merging HITL results into main QA results...")
        
        # Merge HITL results into existing QA results
        json_reporter = JSONReporter()
        
        # Create a minimal report with just HITL results to merge
        hitl_report = json_reporter.aggregate_results(
            hitl_results=results
        )
        
        # Save with merge enabled (will preserve all existing test results)
        json_reporter.save_report(hitl_report, config.QA_RESULTS_JSON, merge_with_existing=True)
        
        # Regenerate PDF from the merged JSON file
        try:
            # Load the merged results from the JSON file
            with open(config.QA_RESULTS_JSON, 'r', encoding='utf-8') as f:
                merged_results = json.load(f)
            
            pdf_reporter = PDFReporter()
            pdf_reporter.generate_report(merged_results, config.QA_REPORT_PDF)
            print("[INFO] PDF report updated successfully")
        except Exception as e:
            print(f"[WARNING] Could not regenerate PDF: {e}")
        
        print(f"\n[SUCCESS] HITL results saved to {config.QA_RESULTS_JSON}")
        print(f"[SUCCESS] Total HITL tests: {results['total_tests']} ({results['completed_tests']} completed)")
        
    except Exception as e:
        print(f"[ERROR] Failed to update main QA results: {e}")
        import traceback
        traceback.print_exc()


def main():
    """Main entry point for HITL test runner."""
    parser = argparse.ArgumentParser(description='Run human-in-the-loop evaluation tests')
    parser.add_argument('--test-type', choices=['needle', 'summary', 'routing', 'all'], default='all',
                       help='Type of tests to run')
    
    args = parser.parse_args()
    
    run_hitl_tests(test_type=args.test_type)


if __name__ == "__main__":
    main()
