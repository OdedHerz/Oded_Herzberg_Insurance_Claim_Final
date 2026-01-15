# QA Testing Suite

## Overview

This QA Testing Suite provides comprehensive testing infrastructure for the Insurance Claim Multi-Agent System, following best practices from Anthropic's guide on agent evaluations.

## Features

- **60 Test Questions**: 20 needle + 15 summary + 10 routing + 15 HITL
- **3 Grader Types**: Code-based (regex), Model-based (OpenAI), Human-in-the-loop
- **Smart Caching**: Run agents once, grade multiple times
- **Multi-format Reports**: JSON + PDF outputs

## Directory Structure

```
QA/
├── test_data/              # Test datasets
│   ├── needle_tests.json   # 20 needle agent tests
│   ├── summary_tests.json  # 15 summary agent tests
│   ├── routing_tests.json  # 10 routing tests
│   └── hitl_tests.json     # 15 human-in-loop tests
├── graders/                # Grading implementations
│   ├── code_grader.py      # Regex/pattern matching
│   ├── model_grader.py     # OpenAI LLM judge
│   └── hitl_grader.py      # Interactive human review
├── collectors/             # Answer collection
│   └── answer_collector.py # Runs agents, caches responses
├── reporters/              # Report generation
│   ├── json_reporter.py    # JSON aggregation
│   └── pdf_reporter.py     # PDF visualization
├── results/                # Test outputs (created on first run)
│   ├── cached_answers.json # Agent responses cache
│   ├── qa_results.json     # Aggregated results
│   └── qa_report.pdf       # Visual report
├── run_qa_tests.py         # Main test runner
└── run_hitl_tests.py       # HITL test runner
```

## Quick Start

### From Main Menu

1. Run `python main.py`
2. Select option `4` (QA Testing Suite)
3. Choose your test type:
   - Needle Agent Tests (option 1)
   - Summary Agent Tests (option 2)
   - Routing Agent Tests (option 3)
   - Human-in-the-Loop (option 4)
   - Full Suite (option 5)

### Direct CLI Usage

**Run all tests:**
```bash
python QA/run_qa_tests.py --test-type=all
```

**Run specific agent tests:**
```bash
python QA/run_qa_tests.py --test-type=needle
python QA/run_qa_tests.py --test-type=summary
python QA/run_qa_tests.py --test-type=routing
```

**Use cached answers (faster, no agent re-runs):**
```bash
python QA/run_qa_tests.py --test-type=all --cached
```

**Run only code graders (free, no model API calls):**
```bash
python QA/run_qa_tests.py --code-only --cached
```

**Run only model graders (requires OpenAI API):**
```bash
python QA/run_qa_tests.py --model-only --cached
```

**Run Human-in-the-Loop tests:**
```bash
python QA/run_hitl_tests.py --test-type=all
```

## Test Types

### 1. Needle Agent Tests (20 questions)

Tests precise fact extraction:
- **Times/Dates**: "What time did the collision occur?"
- **Names**: "Who conducted the phone interview?"
- **Numbers**: "What was Sarah's blood pressure?"
- **Measurements**: "How many feet were the skid marks?"
- **Identifiers**: "What is the claim number?"

**Graders:**
- **Code**: Regex patterns for dates, times, numbers, names
- **Model**: Factual accuracy, completeness, precision

### 2. Summary Agent Tests (15 questions)

Tests synthesis and overview generation:
- **Totals**: "What was the total claim value?"
- **Sequences**: "Summarize the events that led to the claim"
- **Outcomes**: "What was the final resolution?"
- **Timelines**: "How long did the claim process take?"

**Graders:**
- **Code**: Key facts and figures presence
- **Model**: Comprehensiveness, coherence, synthesis quality

### 3. Routing Agent Tests (10 questions)

Tests correct query classification:
- 5 questions that should route to "needle"
- 5 questions that should route to "summary"

**Graders:**
- **Code**: Exact route matching (binary pass/fail)

### 4. Human-in-the-Loop Tests (15 questions)

Subjective quality assessment:
- 5 needle questions (clarity, precision, usefulness)
- 5 summary questions (comprehensiveness, coherence)
- 5 routing questions (routing correctness evaluation)

**Graders:**
- **Human**: Interactive 1-5 rating + text feedback

## Grading System

### Code-Based Graders

**Advantages:**
- Fast (instant)
- Free (no API costs)
- Deterministic
- Good for factual validation

**Example checks:**
- Date format: `\b(January|February|...|December)\s+\d{1,2},\s+\d{4}\b`
- Time format: `\b\d{1,2}:\d{2}(:\d{2})?\s*(AM|PM)?\b`
- Currency: `\$?\d{1,3}(,\d{3})*(\.\d{2})?`

### Model-Based Graders (OpenAI)

**Advantages:**
- Evaluates subjective criteria
- Understands semantics
- Provides reasoning
- Good for quality assessment

**Criteria:**
- **Needle**: Factual accuracy, completeness, precision, no hallucination
- **Summary**: Comprehensiveness, coherence, synthesis, relevance

**Cost:** ~$0.001 per test (using GPT-4o-mini)

### Human-in-the-Loop

**Advantages:**
- Gold standard for quality
- Catches subtle issues
- Provides qualitative feedback
- Builds intuition

**Process:**
1. View question + answer
2. Rate 1-5 based on criteria
3. Optional text feedback
4. Results saved incrementally

## Caching Strategy

The suite uses a **two-phase approach**:

### Phase 1: Answer Collection
```bash
# Agents run once, responses cached
python QA/run_qa_tests.py --test-type=all
```

This creates `QA/results/cached_answers.json` with all agent responses.

### Phase 2: Iterative Grading
```bash
# Use cached answers, run graders multiple times
python QA/run_qa_tests.py --cached --code-only
python QA/run_qa_tests.py --cached --model-only
```

**Benefits:**
- Run expensive agents once
- Iterate on grader improvements
- Compare grader types
- Faster development cycle

## Reports

### JSON Report (`qa_results.json`)

Programmatic access to all results:
```json
{
  "overall_scores": {
    "system_score": 0.85,
    "agent_performance": {
      "needle_agent": 0.88,
      "summary_agent": 0.82,
      "routing_agent": 0.95
    }
  },
  "detailed_results": {
    "needle_tests": [...],
    "summary_tests": [...],
    "routing_tests": [...]
  }
}
```

### PDF Report (`qa_report.pdf`)

Visual report with:
- Executive summary page
- Overall system score
- Agent performance breakdown
- Grader comparison
- Detailed test results

## Cost Estimation

### Per Test Run (Full Suite: 60 tests)

**Agent Costs (OpenAI):**
- Needle tests (20): ~$0.01
- Summary tests (15): ~$0.01
- Routing tests (10): ~$0.005
- HITL tests (15): ~$0.005
- **Total agent costs**: ~$0.03

**Grader Costs (OpenAI):**
- Model grading (35 needle + summary tests): ~$0.035
- **Total grader costs**: ~$0.035

**Total per run**: ~$0.065 (agents + graders)

**With caching**: ~$0.035 (graders only, reuse cached answers)

## Configuration

All settings in `Config/config.py`:

```python
# QA Testing Suite Configuration
QA_DIR = "QA"
QA_TEST_DATA_DIR = os.path.join(QA_DIR, "test_data")
QA_RESULTS_DIR = os.path.join(QA_DIR, "results")

# Test Files
QA_NEEDLE_TESTS = os.path.join(QA_TEST_DATA_DIR, "needle_tests.json")
QA_SUMMARY_TESTS = os.path.join(QA_TEST_DATA_DIR, "summary_tests.json")
QA_ROUTING_TESTS = os.path.join(QA_TEST_DATA_DIR, "routing_tests.json")
QA_HITL_TESTS = os.path.join(QA_TEST_DATA_DIR, "hitl_tests.json")

# Results Files
QA_CACHED_ANSWERS = os.path.join(QA_RESULTS_DIR, "cached_answers.json")
QA_RESULTS_JSON = os.path.join(QA_RESULTS_DIR, "qa_results.json")
QA_REPORT_PDF = os.path.join(QA_RESULTS_DIR, "qa_report.pdf")

# Grader Settings
QA_MODEL_DELAY = 1.0  # Seconds between API calls (rate limiting)
```

## Best Practices

### 1. Start with Code Graders
```bash
python QA/run_qa_tests.py --code-only
```
Fast, free baseline to validate tests.

### 2. Add Model Grading
```bash
python QA/run_qa_tests.py --cached
```
Use cached answers to add OpenAI model grading.

### 3. Sample HITL Tests
```bash
python QA/run_hitl_tests.py --test-type=needle
```
Human review a subset for calibration.

### 4. Iterate on Graders
Modify grader logic, re-run with `--cached` to test improvements without re-querying agents.

### 5. Track Over Time
Save reports with timestamps to track improvements:
```bash
cp QA/results/qa_report.pdf QA/results/qa_report_2026-01-14.pdf
```

## Troubleshooting

### "OPENAI_API_KEY not found"
Add to `.env` file:
```
OPENAI_API_KEY=your_openai_api_key_here
```

### "No cached answers found"
Run without `--cached` flag first to collect answers.

### "OpenAI rate limit exceeded"
Increase `QA_MODEL_DELAY` in `Config/config.py` (default: 1.0 seconds).

### Tests fail with agent errors
Ensure indexes are created:
1. Run `python main.py`
2. Select option 2 (Create/Recreate Indexing)

## Extending the Suite

### Add New Test Questions

Edit test files in `QA/test_data/`:
```json
{
  "id": "needle_21",
  "question": "Your new question?",
  "ground_truth": "Expected answer",
  "expected_route": "needle",
  "code_grader_checks": {
    "pattern_name": "regex_pattern"
  },
  "model_grader_criteria": ["accuracy", "completeness"]
}
```

### Add New Graders

Implement in `QA/graders/` following existing patterns:
```python
class CustomGrader:
    def grade_needle_test(self, test, answer):
        # Your grading logic
        return {"score": 0.0, "details": []}
```

## Support

For issues or questions:
1. Check test datasets in `QA/test_data/`
2. Review results in `QA/results/qa_results.json`
3. Check logs during test runs
4. Verify API keys in `.env` file

---

**Version**: 1.0.0  
**Last Updated**: 2026-01-14  
**Based on**: [Anthropic's Demystifying Evals for AI Agents](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents)
