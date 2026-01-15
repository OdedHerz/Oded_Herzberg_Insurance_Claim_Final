"""
Configuration management for the Insurance Claim Indexing System
Loads environment variables and provides configuration constants
"""

import os
import re
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# OpenAI Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY not found in environment variables. Please check your .env file.")

# Google AI (Gemini) Configuration for RAGAS Evaluation
GOOGLE_AI_API_KEY = os.getenv("GOOGLE_AI_API_KEY")
GEMINI_MODEL = "models/gemini-flash-latest"  # Latest Gemini Flash model

# Supabase Configuration
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
SUPABASE_DB_PASSWORD = os.getenv("SUPABASE_DB_PASSWORD")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in environment variables. Please check your .env file.")

if not SUPABASE_DB_PASSWORD:
    raise ValueError("SUPABASE_DB_PASSWORD must be set in environment variables. Please check your .env file.")

# Chunking Configuration
CHUNK_SIZE = 400  # Small chunks for precise retrieval
CHUNK_OVERLAP = 50  # Overlap between chunks
MIN_CHUNK_SIZE = 200  # Minimum size for tail chunks (merge if smaller)

# Auto-Merging Configuration
AUTO_MERGE_THRESHOLD = 3  # Number of chunks from same parent needed to trigger merge

# Retrieval Configuration
NEEDLE_TOP_K = 6  # Number of chunks to retrieve for needle queries
SUMMARY_TOP_K = 6  # Total summaries to retrieve (Overview + top ranked detail pages)

# OpenAI Model Configuration
EMBEDDING_MODEL = "text-embedding-3-small"  # 1536 dimensions
EMBEDDING_DIMENSIONS = 1536
SUMMARY_MODEL = "gpt-4o-mini"  # For generating summaries
TEMPERATURE = 0.1  # Low temperature for consistent summaries

# File Paths
DATA_DIR = "Data"
PDF_PATH = os.path.join(DATA_DIR, "insurance_claim.pdf")  # 10 pages
METADATA_PATH = os.path.join(DATA_DIR, "claim_metadata.json")  # 10 pages
DOCSTORE_PATH = os.path.join("Indexing", "docstore.json")  # Local document store for parent nodes

# Supabase Table Names
CHUNKS_TABLE = "claim_chunks"
SUMMARIES_TABLE = "claim_summaries"

# PostgreSQL Connection String for Supabase (using Connection Pooler)
# Note: Supabase deprecated direct IPv4 connections - must use pooler now
SUPABASE_POOLER_HOST = os.getenv("SUPABASE_POOLER_HOST", "aws-0-us-east-1.pooler.supabase.com")
SUPABASE_POOLER_PORT = os.getenv("SUPABASE_POOLER_PORT", "6543")

def get_postgres_connection_string():
    """Build PostgreSQL connection string using Supabase Connection Pooler (Transaction Mode)"""
    # Extract project reference from Supabase URL
    # Example: https://kssdybrlodgkjopindol.supabase.co -> project ref is kssdybrlodgkjopindol
    match = re.search(r'https://([^.]+)\.supabase\.co', SUPABASE_URL)
    if match:
        project_ref = match.group(1)
        # New format: postgresql://postgres.[PROJECT-REF]:[PASSWORD]@[POOLER-HOST]:[PORT]/postgres
        return f"postgresql://postgres.{project_ref}:{SUPABASE_DB_PASSWORD}@{SUPABASE_POOLER_HOST}:{SUPABASE_POOLER_PORT}/postgres"
    else:
        raise ValueError("Could not parse SUPABASE_URL to extract project reference")

# Index Names (stored in Indexing folder)
NEEDLE_INDEX_PATH = os.path.join("Indexing", "needle_index")  # For needle-in-a-haystack retrieval
SUMMARY_INDEX_PATH = os.path.join("Indexing", "summary_index")

# RAGAS Evaluation Paths
EVALUATION_DIR = "Evaluation"
QUERY_RESULTS_PATH = os.path.join(EVALUATION_DIR, "query_results.json")
EVALUATION_RESULTS_PATH = os.path.join(EVALUATION_DIR, "evaluation_results.json")
EVALUATION_REPORT_PATH = os.path.join(EVALUATION_DIR, "evaluation_report.pdf")

# QA Testing Suite Configuration
QA_DIR = "QA"
QA_TEST_DATA_DIR = os.path.join(QA_DIR, "test_data")
QA_RESULTS_DIR = os.path.join(QA_DIR, "results")

# QA Test Files
QA_NEEDLE_TESTS = os.path.join(QA_TEST_DATA_DIR, "needle_tests.json")
QA_SUMMARY_TESTS = os.path.join(QA_TEST_DATA_DIR, "summary_tests.json")
QA_ROUTING_TESTS = os.path.join(QA_TEST_DATA_DIR, "routing_tests.json")
QA_HITL_TESTS = os.path.join(QA_TEST_DATA_DIR, "hitl_tests.json")

# QA Results Files
QA_CACHED_ANSWERS = os.path.join(QA_RESULTS_DIR, "cached_answers.json")
QA_RESULTS_JSON = os.path.join(QA_RESULTS_DIR, "qa_results.json")
QA_REPORT_PDF = os.path.join(QA_RESULTS_DIR, "qa_report.pdf")

# QA Grader Configuration
QA_CODE_GRADER_ENABLED = True
QA_MODEL_GRADER_ENABLED = True  # Uses Gemini
QA_HITL_GRADER_ENABLED = True

# QA Model Grader Settings (uses same Gemini as RAGAS)
QA_GEMINI_DELAY = 1.0  # Seconds between Gemini API calls (rate limiting)

def validate_config():
    """Validate that all required configuration is present"""
    errors = []
    
    if not OPENAI_API_KEY:
        errors.append("OPENAI_API_KEY is missing")
    
    if not SUPABASE_URL:
        errors.append("SUPABASE_URL is missing")
        
    if not SUPABASE_KEY:
        errors.append("SUPABASE_KEY is missing")
    
    # Note: GOOGLE_AI_API_KEY is optional (only needed for RAGAS evaluation)
    
    if errors:
        raise ValueError(f"Configuration errors: {', '.join(errors)}")
    
    print("[OK] Configuration validated successfully")
    return True

if __name__ == "__main__":
    # Test configuration
    print("=" * 60)
    print("Configuration Test")
    print("=" * 60)
    
    try:
        validate_config()
        print(f"\nOpenAI API Key: {OPENAI_API_KEY[:20]}...")
        print(f"Supabase URL: {SUPABASE_URL}")
        print(f"Supabase Key: {SUPABASE_KEY[:20]}...")
        print(f"\nChunk Size: {CHUNK_SIZE}")
        print(f"Chunk Overlap: {CHUNK_OVERLAP}")
        print(f"Embedding Model: {EMBEDDING_MODEL}")
        print(f"Summary Model: {SUMMARY_MODEL}")
        print("\n[OK] All configuration loaded successfully!")
    except Exception as e:
        print(f"\n[ERROR] Configuration error: {e}")
        print("\nPlease make sure you have created a .env file with:")
        print("  - OPENAI_API_KEY")
        print("  - SUPABASE_URL")
        print("  - SUPABASE_KEY")


