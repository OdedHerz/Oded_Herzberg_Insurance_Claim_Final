"""
QA Suite Installation Validator

Checks if all required files and components are in place.
"""

import sys
from pathlib import Path
import json

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))


def check_file_exists(file_path: str, description: str) -> bool:
    """Check if a file exists and report result."""
    path = Path(__file__).parent.parent / file_path
    exists = path.exists()
    
    status = "[OK]" if exists else "[MISSING]"
    print(f"  {status} {description}: {file_path}")
    
    return exists


def check_directory_exists(dir_path: str, description: str) -> bool:
    """Check if a directory exists and report result."""
    path = Path(__file__).parent.parent / dir_path
    exists = path.is_dir()
    
    status = "[OK]" if exists else "[MISSING]"
    print(f"  {status} {description}: {dir_path}")
    
    return exists


def validate_test_dataset(file_path: str, expected_count: int) -> bool:
    """Validate a test dataset file."""
    try:
        path = Path(__file__).parent.parent / file_path
        with open(path, 'r') as f:
            data = json.load(f)
        
        tests = data.get('tests', [])
        actual_count = len(tests)
        
        if actual_count >= expected_count:
            print(f"    [OK] Contains {actual_count} tests (expected >={expected_count})")
            return True
        else:
            print(f"    [ERROR] Contains only {actual_count} tests (expected >={expected_count})")
            return False
    
    except Exception as e:
        print(f"    [ERROR] Error reading file: {e}")
        return False


def validate_python_imports():
    """Validate that all required Python packages can be imported."""
    print("\n" + "=" * 70)
    print("VALIDATING PYTHON PACKAGES")
    print("=" * 70)
    
    all_ok = True
    
    packages = [
        ('reportlab', 'ReportLab (PDF generation)'),
        ('google.generativeai', 'Google Generative AI (Gemini)'),
        ('openai', 'OpenAI'),
        ('supabase', 'Supabase'),
        ('numpy', 'NumPy')
    ]
    
    for package, description in packages:
        try:
            __import__(package)
            print(f"  [OK] {description}")
        except ImportError:
            print(f"  [MISSING] {description} - NOT INSTALLED")
            all_ok = False
    
    return all_ok


def main():
    """Run full validation check."""
    print("\n" + "=" * 70)
    print("QA TESTING SUITE - INSTALLATION VALIDATION")
    print("=" * 70)
    
    all_checks_passed = True
    
    # Check directory structure
    print("\n" + "=" * 70)
    print("CHECKING DIRECTORY STRUCTURE")
    print("=" * 70)
    
    dirs = [
        ("QA", "Main QA directory"),
        ("QA/test_data", "Test datasets directory"),
        ("QA/graders", "Graders directory"),
        ("QA/collectors", "Collectors directory"),
        ("QA/reporters", "Reporters directory")
    ]
    
    for dir_path, desc in dirs:
        if not check_directory_exists(dir_path, desc):
            all_checks_passed = False
    
    # Check test datasets
    print("\n" + "=" * 70)
    print("CHECKING TEST DATASETS")
    print("=" * 70)
    
    datasets = [
        ("QA/test_data/needle_tests.json", "Needle tests", 20),
        ("QA/test_data/summary_tests.json", "Summary tests", 15),
        ("QA/test_data/routing_tests.json", "Routing tests", 10),
        ("QA/test_data/hitl_tests.json", "HITL tests", 10)
    ]
    
    for file_path, desc, expected_count in datasets:
        if check_file_exists(file_path, desc):
            if not validate_test_dataset(file_path, expected_count):
                all_checks_passed = False
        else:
            all_checks_passed = False
    
    # Check graders
    print("\n" + "=" * 70)
    print("CHECKING GRADERS")
    print("=" * 70)
    
    graders = [
        ("QA/graders/__init__.py", "Graders module init"),
        ("QA/graders/code_grader.py", "Code grader"),
        ("QA/graders/model_grader.py", "Model grader (Gemini)"),
        ("QA/graders/hitl_grader.py", "HITL grader")
    ]
    
    for file_path, desc in graders:
        if not check_file_exists(file_path, desc):
            all_checks_passed = False
    
    # Check collectors
    print("\n" + "=" * 70)
    print("CHECKING COLLECTORS")
    print("=" * 70)
    
    collectors = [
        ("QA/collectors/__init__.py", "Collectors module init"),
        ("QA/collectors/answer_collector.py", "Answer collector")
    ]
    
    for file_path, desc in collectors:
        if not check_file_exists(file_path, desc):
            all_checks_passed = False
    
    # Check reporters
    print("\n" + "=" * 70)
    print("CHECKING REPORTERS")
    print("=" * 70)
    
    reporters = [
        ("QA/reporters/__init__.py", "Reporters module init"),
        ("QA/reporters/json_reporter.py", "JSON reporter"),
        ("QA/reporters/pdf_reporter.py", "PDF reporter")
    ]
    
    for file_path, desc in reporters:
        if not check_file_exists(file_path, desc):
            all_checks_passed = False
    
    # Check CLI scripts
    print("\n" + "=" * 70)
    print("CHECKING CLI SCRIPTS")
    print("=" * 70)
    
    scripts = [
        ("QA/run_qa_tests.py", "Main test runner"),
        ("QA/run_hitl_tests.py", "HITL test runner"),
        ("QA/README.md", "QA suite documentation")
    ]
    
    for file_path, desc in scripts:
        if not check_file_exists(file_path, desc):
            all_checks_passed = False
    
    # Check configuration
    print("\n" + "=" * 70)
    print("CHECKING CONFIGURATION")
    print("=" * 70)
    
    try:
        from Config import config
        
        attrs = [
            ('QA_DIR', 'QA directory path'),
            ('QA_TEST_DATA_DIR', 'Test data directory path'),
            ('QA_RESULTS_DIR', 'Results directory path'),
            ('QA_NEEDLE_TESTS', 'Needle tests path'),
            ('QA_SUMMARY_TESTS', 'Summary tests path'),
            ('QA_ROUTING_TESTS', 'Routing tests path'),
            ('QA_HITL_TESTS', 'HITL tests path'),
            ('QA_CACHED_ANSWERS', 'Cached answers path'),
            ('QA_RESULTS_JSON', 'Results JSON path'),
            ('QA_REPORT_PDF', 'Report PDF path')
        ]
        
        for attr, desc in attrs:
            if hasattr(config, attr):
                print(f"  [OK] {desc} ({attr})")
            else:
                print(f"  [MISSING] {desc} ({attr}) - NOT FOUND")
                all_checks_passed = False
    
    except Exception as e:
        print(f"  [ERROR] Error importing config: {e}")
        all_checks_passed = False
    
    # Check Python packages
    if not validate_python_imports():
        all_checks_passed = False
    
    # Final summary
    print("\n" + "=" * 70)
    print("VALIDATION SUMMARY")
    print("=" * 70)
    
    if all_checks_passed:
        print("\n[SUCCESS] ALL CHECKS PASSED!")
        print("\nYour QA Testing Suite is ready to use.")
        print("\nNext steps:")
        print("  1. Ensure your .env file has GOOGLE_AI_API_KEY set")
        print("  2. Run 'python main.py' and select option 4 (QA Testing Suite)")
        print("  3. Or run directly: 'python QA/run_qa_tests.py --test-type=all'")
        print("\nFor more information, see QA/README.md")
    else:
        print("\n[FAILED] SOME CHECKS FAILED")
        print("\nPlease fix the issues above before running the QA suite.")
        print("See QA/README.md for setup instructions.")
    
    print("\n" + "=" * 70)
    
    return 0 if all_checks_passed else 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
