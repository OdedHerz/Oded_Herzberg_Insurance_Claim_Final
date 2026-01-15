"""
QA Test Runner - Main CLI script for running QA tests

This script orchestrates the entire QA testing process:
1. Load test datasets
2. Collect agent answers (or use cached)
3. Run code and/or model graders
4. Generate JSON and PDF reports
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
from QA.graders.code_grader import CodeGrader
from QA.graders.model_grader import ModelGrader
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
        
        # Display metadata if available
        if '_metadata' in cached:
            metadata = cached['_metadata']
            last_updated = metadata.get('last_updated', 'Unknown')
            print(f"[INFO] Loaded cached answers from {cache_file}")
            print(f"[INFO] Cache last updated: {last_updated}")
        else:
            print(f"[INFO] Loaded cached answers from {cache_file} (no timestamp)")
        
        return cached
    except FileNotFoundError:
        print(f"[INFO] No cached answers found at {cache_file}")
        return {}
    except Exception as e:
        print(f"[ERROR] Failed to load cached answers: {e}")
        return {}


def save_cached_answers(answers: dict, cache_file: str):
    """
    Save answers to cache file with metadata, merging with existing cache.
    
    This function:
    1. Loads existing cached answers (if any)
    2. Merges new answers with existing ones
    3. Updates metadata timestamp
    4. Saves the merged result
    
    This ensures that running needle tests doesn't delete summary test cache, etc.
    """
    try:
        Path(cache_file).parent.mkdir(parents=True, exist_ok=True)
        
        # Load existing cache (if it exists)
        existing_cache = load_cached_answers(cache_file)
        
        # Merge: new answers override existing ones for the same test type
        for test_type in ['needle_answers', 'summary_answers', 'routing_answers']:
            if test_type in answers:
                if test_type not in existing_cache:
                    existing_cache[test_type] = {}
                
                # Update each test individually with timestamp
                for test_id, test_data in answers[test_type].items():
                    # Add individual test timestamp
                    test_data['cached_at'] = datetime.now().isoformat()
                    existing_cache[test_type][test_id] = test_data
        
        # Update metadata with global timestamp
        existing_cache['_metadata'] = {
            "last_updated": datetime.now().isoformat(),
            "version": "1.0.0",
            "description": "Cached answers from QA test runs"
        }
        
        with open(cache_file, 'w', encoding='utf-8') as f:
            json.dump(existing_cache, f, indent=2, ensure_ascii=False)
        
        # Report what was saved
        test_types_saved = [t.replace('_', ' ').title() for t in ['needle_answers', 'summary_answers', 'routing_answers'] if t in answers]
        print(f"[INFO] Saved cached answers to {cache_file}")
        print(f"[INFO] Updated: {', '.join(test_types_saved)}")
        print(f"[INFO] Cache updated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    except Exception as e:
        print(f"[ERROR] Failed to save cached answers: {e}")


def run_needle_tests(use_cached: bool = False, code_only: bool = False, model_only: bool = False):
    """Run needle agent tests with code and/or model graders."""
    print("\n" + "=" * 70)
    print("RUNNING NEEDLE AGENT TESTS")
    print("=" * 70)
    
    # Load tests
    tests = load_test_dataset(config.QA_NEEDLE_TESTS)
    if not tests:
        return None
    
    # Get or collect answers
    cache_file = config.QA_CACHED_ANSWERS
    # Always load existing cache to preserve other test types
    cached_data = load_cached_answers(cache_file)
    
    if use_cached and 'needle_answers' in cached_data:
        print("[INFO] Using cached needle answers")
        answers_dict = cached_data['needle_answers']
    else:
        print("[INFO] Collecting fresh needle answers from agents...")
        collector = AnswerCollector()
        answers_dict = collector.collect_needle_answers(tests, verbose=True)
        
        # Update cache (will merge with existing cache in save function)
        cached_data['needle_answers'] = answers_dict
        save_cached_answers(cached_data, cache_file)
    
    results = {}
    
    # Run code grader
    if not model_only:
        print("\n[CODE GRADER] Grading needle tests...")
        code_grader = CodeGrader()
        code_results = code_grader.grade_batch(tests, answers_dict, 'needle')
        results['code_results'] = code_results
        print(f"[CODE GRADER] Average score: {code_results['average_score']:.3f}")
    
    # Run model grader
    if not code_only:
        print("\n[MODEL GRADER] Grading needle tests with LLM judge...")
        model_grader = ModelGrader()
        model_results = model_grader.grade_batch(tests, answers_dict, 'needle', delay_between_calls=config.QA_GEMINI_DELAY)
        results['model_results'] = model_results
        print(f"[MODEL GRADER] Average score: {model_results['average_score']:.3f}")
    
    return results


def run_summary_tests(use_cached: bool = False):
    """Run summary agent tests with model grader (semantic evaluation only)."""
    print("\n" + "=" * 70)
    print("RUNNING SUMMARY AGENT TESTS (Model Grader Only)")
    print("=" * 70)
    print("[INFO] Summary tests use only model grader for semantic evaluation")
    
    # Load tests
    tests = load_test_dataset(config.QA_SUMMARY_TESTS)
    if not tests:
        return None
    
    # Get or collect answers
    cache_file = config.QA_CACHED_ANSWERS
    # Always load existing cache to preserve other test types
    cached_data = load_cached_answers(cache_file)
    
    if use_cached and 'summary_answers' in cached_data:
        print("[INFO] Using cached summary answers")
        answers_dict = cached_data['summary_answers']
    else:
        print("[INFO] Collecting fresh summary answers from agents...")
        collector = AnswerCollector()
        answers_dict = collector.collect_summary_answers(tests, verbose=True)
        
        # Update cache (will merge with existing cache in save function)
        cached_data['summary_answers'] = answers_dict
        save_cached_answers(cached_data, cache_file)
    
    results = {}
    
    # Run model grader only (summaries require semantic evaluation, not pattern matching)
    print("\n[MODEL GRADER] Grading summary tests with LLM judge...")
    model_grader = ModelGrader()
    model_results = model_grader.grade_batch(tests, answers_dict, 'summary', delay_between_calls=config.QA_GEMINI_DELAY)
    results['model_results'] = model_results
    print(f"[MODEL GRADER] Average score: {model_results['average_score']:.3f}")
    
    return results


def run_routing_tests(use_cached: bool = False):
    """Run routing agent tests."""
    print("\n" + "=" * 70)
    print("RUNNING ROUTING AGENT TESTS")
    print("=" * 70)
    
    # Load tests
    tests = load_test_dataset(config.QA_ROUTING_TESTS)
    if not tests:
        return None
    
    # Get or collect answers
    cache_file = config.QA_CACHED_ANSWERS
    # Always load existing cache to preserve other test types
    cached_data = load_cached_answers(cache_file)
    
    if use_cached and 'routing_answers' in cached_data:
        print("[INFO] Using cached routing answers")
        answers_dict = cached_data['routing_answers']
    else:
        print("[INFO] Collecting fresh routing decisions from agents...")
        collector = AnswerCollector()
        answers_dict = collector.collect_routing_answers(tests, verbose=True)
        
        # Update cache (will merge with existing cache in save function)
        cached_data['routing_answers'] = answers_dict
        save_cached_answers(cached_data, cache_file)
    
    # Run code grader
    print("\n[CODE GRADER] Grading routing tests...")
    code_grader = CodeGrader()
    routing_results = code_grader.grade_batch(tests, answers_dict, 'routing')
    print(f"[CODE GRADER] Routing accuracy: {routing_results['average_score']:.1%}")
    
    return routing_results


def main():
    """Main entry point for QA test runner."""
    parser = argparse.ArgumentParser(description='Run QA tests for the multi-agent system')
    parser.add_argument('--test-type', choices=['needle', 'summary', 'routing', 'all'], default='all',
                       help='Type of tests to run')
    parser.add_argument('--code-only', action='store_true',
                       help='Run only code-based graders (applies to needle tests only)')
    parser.add_argument('--model-only', action='store_true',
                       help='Run only model-based graders (applies to needle tests only, summary always uses model)')
    parser.add_argument('--cached', action='store_true',
                       help='Use cached answers if available')
    parser.add_argument('--no-pdf', action='store_true',
                       help='Skip PDF report generation')
    parser.add_argument('--clear-results', action='store_true',
                       help='Clear previous test results before running (start fresh)')
    
    args = parser.parse_args()
    
    # Validate arguments
    if args.code_only and args.model_only:
        print("[ERROR] Cannot specify both --code-only and --model-only")
        return
    
    print("\n" + "=" * 70)
    print("QA TESTING SUITE")
    print("=" * 70)
    print(f"Test Type: {args.test_type}")
    print(f"Graders: {'Code only' if args.code_only else 'Model only' if args.model_only else 'Code + Model'}")
    print(f"Use Cached: {args.cached}")
    print(f"Merge Results: {'No (starting fresh)' if args.clear_results else 'Yes (accumulate with previous)'}")
    print("=" * 70)
    
    all_results = {}
    
    # Run tests based on type
    if args.test_type in ['needle', 'all']:
        needle_results = run_needle_tests(use_cached=args.cached, code_only=args.code_only, model_only=args.model_only)
        if needle_results:
            all_results['needle'] = needle_results
    
    if args.test_type in ['summary', 'all']:
        # Summary tests only use model grader (no code_only/model_only options)
        summary_results = run_summary_tests(use_cached=args.cached)
        if summary_results:
            all_results['summary'] = summary_results
    
    if args.test_type in ['routing', 'all']:
        routing_results = run_routing_tests(use_cached=args.cached)
        if routing_results:
            all_results['routing'] = routing_results
    
    # Generate reports
    if all_results:
        print("\n" + "=" * 70)
        print("GENERATING REPORTS")
        print("=" * 70)
        
        # Aggregate results
        json_reporter = JSONReporter()
        report = json_reporter.aggregate_results(
            needle_code_results=all_results.get('needle', {}).get('code_results'),
            needle_model_results=all_results.get('needle', {}).get('model_results'),
            summary_code_results=all_results.get('summary', {}).get('code_results'),
            summary_model_results=all_results.get('summary', {}).get('model_results'),
            routing_results=all_results.get('routing')
        )
        
        # Save JSON report (merge with existing unless --clear-results is specified)
        json_reporter.save_report(report, config.QA_RESULTS_JSON, merge_with_existing=not args.clear_results)
        
        # Generate PDF report from the merged JSON results
        if not args.no_pdf:
            try:
                # Load the merged results from the JSON file (which includes all test types)
                with open(config.QA_RESULTS_JSON, 'r', encoding='utf-8') as f:
                    merged_results = json.load(f)
                
                pdf_reporter = PDFReporter()
                pdf_reporter.generate_report(merged_results, config.QA_REPORT_PDF)
            except Exception as e:
                print(f"[ERROR] Failed to generate PDF report: {e}")
                print("[INFO] JSON report saved successfully")
        
        print("\n" + "=" * 70)
        print("QA TESTING COMPLETE")
        print("=" * 70)
        print(f"Results saved to:")
        print(f"  - JSON: {config.QA_RESULTS_JSON}")
        if not args.no_pdf:
            print(f"  - PDF: {config.QA_REPORT_PDF}")
        print("=" * 70)
    else:
        print("\n[ERROR] No test results to report")


if __name__ == "__main__":
    main()
