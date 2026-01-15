Oded Herzberg

# Insurance Claim Information Retrieval System

**Midterm Coding Assignment - GenAI + Multi-Agent Orchestration**

A multi-agent RAG system for answering questions about insurance claims using specialized retrieval strategies.

---

## 📋 Table of Contents

1. [Project Overview](#project-overview)
2. [System Architecture](#system-architecture)
3. [Indexing Strategy](#indexing-strategy)
4. [Agent System](#agent-system)
5. [MCP Discussion](#mcp-discussion)
6. [Evaluation](#evaluation)
7. [QA Testing Suite](#qa-testing-suite)
8. [Quick Start](#quick-start)

---

## 📖 Project Overview

This system answers questions about insurance claims using three specialized agents:
- **Router Agent**:  Classifies questions as summary or needle queries
- **Needle Agent**:  Finds specific facts using small chunk retrieval
- **Summary Agent**: Provides overviews using page-level summaries

### Key Features

- 10-page insurance claim document with chronological information
- Needle index with auto-merge for adaptive context
- Summary index with always-include overview pages
- Multi-agent orchestration with GPT-4o-mini
- RAGAS evaluation with Gemini as judge

### Technology Stack

- **LLM**: OpenAI GPT-4o-mini
- **Embeddings**: OpenAI text-embedding-3-small (1536 dims)
- **Database**: Supabase (PostgreSQL + pgvector)
- **Evaluation**: RAGAS + Google Gemini
- **Framework**: LlamaIndex

---

## 🏗️ System Architecture

### Flow Diagram

```
User Query
    ↓
Routing Agent (Classify: SUMMARY or NEEDLE)
    ↓
    ├─→ [NEEDLE] → Needle Agent → Vector Search (Supabase)
    │                                ↓
    │                    Retrieve top-6 similar chunks
    │                                ↓
    │                    Auto-Merge (if ≥3 chunks from same parent)
    │                                ↓
    │                    Add full parent page from docstore to context
    │
    └─→ [SUMMARY] → Summary Agent → Vector Search (Supabase)
                                ↓
                    Retrieve page summaries: Overview (1, 10) + top-4 of detailed pages
    ↓
Final Answer (GPT-4o-mini)
```

### System Components

```
Project/
├── Data/                      # Document generation (10-page PDF)
├── Indexing/                  # Needle & summary indexes
├── Agents/                    # Router, needle, summary agents
├── Evaluation/                # RAGAS framework
├── Config/                    # System parameters
└── main.py                    # Interactive menu
```

---

## 📊 Indexing Strategy

### Document Structure

**File**: `Data/insurance_claim.pdf` (10 pages)

- **Timeline**:     January 15 – February 5, 2024
- **Page Types**:   Overview (Pages 1, 10) + Details (Pages 2-9)
- **Metadata**:     Header, date, involved parties, page type
- **Precision**:    Second-level timestamps (e.g., 09:23:45 AM)

### 1. Needle Index (For Specific Facts)

**Purpose**: Retrieve precise information using small chunks

**Strategy**:

| Parameter     | Value              | Rationale 
|---------------|--------------------|-----------
| Chunk Size    | 400 chars          | Balances precision with context 
| Overlap       | 50 chars           | Preserves sentence continuity across chunks 
| Hierarchy     | 2 levels           | Chunks → Parent pages 
| Auto-Merge    | ≥3 chunks          | Adds parent if multiple chunks from same page
| Metadata      | Date, header, type | Provides temporal/structural context 
| Min Chunk     | 200 chars          | Merges tail chunks if too small


**How It Works**:
1. Split each page into 400-character chunks with 50-char overlap (sentence-aware)
2. Merge tail chunks smaller than 200 chars into previous chunk
3. Store chunks with embeddings in Supabase
4. On query: Retrieve top-6 similar chunks
5. If ≥3 chunks from same parent page → Add full parent for context
6. Pass chunks (+ parent if merged) to LLM


**Why 400-Character Chunks?**
- ✅ High precision for specific facts
- ✅ Less noise in retrieval
- ✅ Better semantic matching
- ✅ Adequate context for most queries
- ✅ Sentence-aware overlap maintains coherence
- ⚠️ May lack broader context (solved by auto-merge)

**Example**: Query "What was Sarah's blood pressure?" retrieves the exact medical assessment chunk.

### 2. Summary Index (For Overviews)

**Purpose**: Answer high-level questions using page summaries

**Strategy**:
- **Map**:               Summarize each page independently (GPT-4o-mini)
- **Reduce**:            Store page-level summaries with embeddings
- **Always Include**:    Overview pages (1, 10) regardless of similarity
- **Retrieval**:         Overview pages + top-4 similar detail pages

**Why Always Include Overview?**
- Page 1: Claim basics (parties, dates, amount)
- Page 10: Final resolution
- Vector similarity alone might miss these critical pages

**Example**: Query "What was the total claim value?" includes Pages 1, 10 + top financial detail pages.

### 3. Vector Similarity

- **Embedding Model**: `text-embedding-3-small`
- **Similarity**:       Cosine similarity
- **Top-K**:            Configurable (Needle: 6, Summary: 6)
- **Storage**:          Supabase with pgvector extension

---

## 🤖 Agent System

### 1. Routing Agent

**Purpose**: Classify queries as SUMMARY or NEEDLE

**LLM**: GPT-4o-mini

**Logic**:
- **SUMMARY**: High-level, overview, timeline questions
- **NEEDLE**:  Specific facts, precise details

**Method**: Example-based prompt with keywords

### 2. Needle Agent

**Purpose**: Answer precise factual questions

**Process**:
1. Embed user query
2. Vector search in chunks (cosine similarity)
3. Retrieve top-6 chunks
4. Check auto-merge: ≥3 chunks from same parent?
5. Build context (chunks + parent if merged)
6. Generate answer with GPT-4o-mini

**Output Style**: Concise, factual, natural language (no "chunk" references)

**Example**:
```
Q: "How many feet were the skid marks?"
A: "The skid marks at the collision scene measured exactly 47 feet 
    from Chen's vehicle trajectory on the wet pavement."
```

### 3. Summary Agent

**Purpose**: Answer high-level overview questions

**Process**:
1. Embed user query
2. Retrieve ALL Overview pages (always)
3. Vector search in Detail pages
4. Combine: Overview + top-4 Detail pages
5. Generate answer with GPT-4o-mini (3-5 sentences)

**Output Style**: Concise but complete, includes key supporting facts

**Example**:
```
Q: "What was the final resolution?"
A: "The claim was resolved on February 5, 2024, with a total payout 
    of $47,850. Sarah Mitchell received $43,510 for vehicle damage 
    and $3,840 for medical expenses. The vehicle was repaired and 
    passed quality inspection."
```

---

## 🔌 MCP Discussion

The assignment required MCP (Model Context Protocol) integration, but OpenAI's Python SDK doesn't natively support MCP protocol (which requires specific client implementations like Claude Desktop). We implemented direct Supabase SDK integration instead, which provides the same functionality (vector search, metadata retrieval) through a more stable and maintainable architecture for OpenAI-based agents.

---

## 📈 Evaluation

### Framework: RAGAS

Industry-standard RAG evaluation with Gemini as LLM judge (independent from system's OpenAI models).

### Metrics (6 Total)

1. **Context Precision**:   Are retrieved chunks relevant?
2. **Context Recall**:      Were correct chunks retrieved?
3. **Faithfulness**:        Is answer grounded in context?
4. **Answer Relevancy**:    Does answer address the question?
5. **Answer Similarity**:   Semantic match to ground truth?
6. **Answer Correctness**:  Factually accurate?

### Test Suite

- **10 test cases**:        5 needle + 5 summary questions
- **Ground truth**:         Manually created from source document
- **Expected chunks**:      Pre-defined for recall measurement
- **Two phases**:           Query phase → Evaluation phase (efficient, no re-runs)

### Results

**Output Files**:
- `query_results.json`: Agent responses and contexts
- `evaluation_results.json`: RAGAS scores
- `evaluation_report.pdf`: Visual performance report

**Example Scores** (from actual evaluation):
```
Overall System: 0.747
├─ Needle Agent: 0.788 (strong precision)
└─ Summary Agent: 0.705 (good synthesis)

Key Strengths:
✓ High faithfulness (low hallucination)
✓ High similarity (semantically correct)
✓ Good answer relevancy
```

---

## ⚠️ Limitations & Trade-offs

### Current Limitations

1. **Single document** (extensible to multi-document with doc_id metadata)
2. **Fixed chunk size** (could implement adaptive chunking)
3. **No caching** (could add Redis for frequent queries)
4. **Synchronous processing** (could implement async for scale)

### Design Trade-offs

**Chunk Size (400 chars)**:
- Smaller (<300) = Higher precision ✓, Missing context ⚠️
- Current (400) = Good balance ✓, Sentence-aware ✓
- Larger (>600) = More context ✓, Lower precision ⚠️
- **Choice**: Optimal for insurance document granularity

**Auto-Merge Threshold (3)**:
- Low = More context, Higher cost
- High = Less merging, Possible info loss
- **Choice**: Requires strong signal before adding parent

**Summary Style (3-5 sentences)**:
- Brief = Fast, May miss details
- Verbose = Complete, Poor UX
- **Choice**: Concise but complete

---

## 🚀 Quick Start

### Prerequisites

- Python 3.9+
- OpenAI API key
- Supabase account (with pgvector)
- Google AI API key (for evaluation)

### Installation

```bash
# Install all dependencies
pip install -r requirements.txt

# Setup environment (.env file)
OPENAI_API_KEY       =your-key
SUPABASE_URL         =your-url
SUPABASE_KEY         =your-key
SUPABASE_DB_PASSWORD =your-password
GOOGLE_AI_API_KEY    =your-key  # Optional (evaluation only)
```

### Setup Database

The system **automatically creates required tables** when you run the indexing process for the first time. No manual SQL setup needed!

The system automatically creates tables with this schema:

```sql
-- claim_chunks: stores small text chunks for needle queries
CREATE TABLE claim_chunks (
  chunk_id TEXT PRIMARY KEY,
  content TEXT NOT NULL,
  embedding VECTOR(1536),
  metadata JSONB,
  page_number INTEGER,
  chunk_index INTEGER,
  parent_id TEXT
);

-- claim_summaries: stores page summaries for overview queries
CREATE TABLE claim_summaries (
  summary_id TEXT PRIMARY KEY,
  content TEXT NOT NULL,
  embedding VECTOR(1536),
  metadata JSONB,
  page_number INTEGER,
  summary_type TEXT
);
```

### Run System

```bash
python main.py
```

**First Time Setup**: Use menu Option 2 to create indexes before asking questions.

**Menu Options**:
1. Ask a Question
2. Create/Recreate Indexing
3. RAGAS Evaluation
4. Exit

### Example Queries

**Needle**:
- "What is the claim number?"
- "What was Sarah's blood pressure?"
- "How many feet were the skid marks?"

**Summary**:
- "What was the total claim value?"
- "Who was at fault and why?"
- "What was the final resolution?"

---

## 📁 Project Structure

```
insurance-claim-rag-system/
│
├── Data/
│   ├── generate_claim_pdf.py     # Creates 10-page claim
│   ├── insurance_claim.pdf       # Generated document
│   └── claim_metadata.json       # Page metadata
│
├── Indexing/
│   ├── needle_indexing.py        # Needle index
│   ├── summary_indexing.py       # Summary index
│   └── [index files]             # Vector storage
│
├── Agents/
│   ├── routing_agent.py          # Query classifier
│   ├── needle_agent.py           # Precise retrieval
│   └── summary_agent.py          # Overview generation
│
├── Evaluation/
│   ├── evaluate.py               # RAGAS runner
│   ├── test_dataset.json         # 10 test cases
│   ├── evaluation_report.pdf     # Performance report
│   └── [results files]           # JSON outputs
│
├── QA/                            # QA Testing Suite
│   ├── test_data/                # Test datasets (60 tests)
│   ├── graders/                  # Code/model/HITL graders
│   ├── collectors/               # Answer collection
│   ├── reporters/                # JSON/PDF reporters
│   ├── results/                  # Test outputs
│   ├── run_qa_tests.py           # Main test runner
│   ├── run_hitl_tests.py         # HITL runner
│   └── README.md                 # QA documentation
│
├── Config/
│   └── config.py                 # System parameters
│
├── main.py                        # Main orchestrator
├── README.md                      # This file
└── requirements.txt               # Dependencies
```

---

## 🧪 QA Testing Suite

A comprehensive quality assurance framework for testing all agents in the system with **60 test questions** and **3 grader types**.

### Key Features

- **60 Test Questions**: 20 needle + 15 summary + 10 routing + 15 HITL
- **3 Grader Types**: Code-based (regex), Model-based (OpenAI), Human-in-the-loop
- **Smart Caching**: Run agents once, grade multiple times
- **Multi-format Reports**: JSON + PDF outputs

### Quick Start

```bash
# Run from main menu
python main.py  # Select option 4 (QA Testing Suite)

# Or run directly
python QA/run_qa_tests.py --test-type=all

# Use cached answers (faster, no agent re-runs)
python QA/run_qa_tests.py --cached --code-only
```

### Cost Estimation

| Mode | Tests | Duration | Cost |
|------|-------|----------|------|
| Code-only | 60 | 3 min | ~$0.03 (agents only) |
| Full Suite | 60 | 25 min | ~$0.08 (agents + graders) |
| Cached | 60 | 2 min | ~$0.05 (graders only) |

### Documentation

**See [`QA/README.md`](QA/README.md)** for comprehensive documentation including:
- Detailed test descriptions
- Grader implementations
- CLI usage and options
- Caching strategy
- Report formats
- Extending the suite

---

## 📝 Additional Documentation

## 🎯 Assignment Coverage

✅ **10-page insurance claim** with chronological information  
✅ **Needle indexing** with auto-merge (chunks → parent pages)  
✅ **Summary index** with MapReduce strategy  
✅ **Three agents** (router, needle, summary) with specialized retrieval  
✅ **MCP discussion** (investigated, explained limitation)  
✅ **Agent diagram** (see `ARCHITECTURE_DIAGRAM.md`)  
✅ **RAGAS evaluation** (6 metrics, 10 tests, Gemini judge)  
✅ **Comprehensive documentation**  

---

## 💡 Key Innovations

1. **Auto-Merge**: Adaptive context based on chunk patterns
2. **Always-Include Overview**: Smart summary retrieval
3. **Two-Phase Evaluation**: Efficient RAGAS workflow
4. **Production-Ready**: Error handling, config management, modular design
