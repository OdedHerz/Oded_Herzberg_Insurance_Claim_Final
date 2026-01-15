"""
Semi-Automatic Question Generator for RAGAS Evaluation

This script generates candidate test questions from the insurance claim PDF
by analyzing each page and suggesting both needle (specific details) and
summary (high-level) questions.
"""

import json
import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from llama_index.core import SimpleDirectoryReader
from openai import OpenAI
from Config import config


def load_pdf_pages():
    """Load PDF pages with metadata."""
    print("[OK] Loading PDF pages...")
    
    # Load metadata
    with open(config.METADATA_PATH, 'r', encoding='utf-8') as f:
        metadata = json.load(f)
    
    # Load PDF
    reader = SimpleDirectoryReader(
        input_files=[config.PDF_PATH],
        filename_as_id=True
    )
    documents = reader.load_data()
    
    # Enrich with metadata
    enriched_pages = []
    for doc in documents:
        page_num = doc.metadata.get('page_label', '1')
        page_key = f"page_{page_num}"
        
        if page_key in metadata:
            doc.metadata.update(metadata[page_key])
            enriched_pages.append({
                'page_number': int(page_num),
                'content': doc.text,
                'metadata': metadata[page_key]
            })
    
    print(f"[OK] Loaded {len(enriched_pages)} pages")
    return enriched_pages


def generate_questions_for_page(page, client, needle_count=1, summary_count=0):
    """
    Generate candidate questions for a single page using OpenAI.
    
    Args:
        page: Page dictionary with content and metadata
        client: OpenAI client
        needle_count: Number of needle questions to generate
        summary_count: Number of summary questions to generate
    
    Returns:
        List of question dictionaries
    """
    page_num = page['page_number']
    content = page['content']
    metadata = page['metadata']
    
    questions = []
    
    # Generate needle questions (specific details)
    if needle_count > 0:
        needle_prompt = f"""You are creating test questions for a RAG system evaluation.

Page {page_num} - {metadata['header']}
Date: {metadata['date']}
Type: {metadata['type']}

Content:
{content}

Generate {needle_count} specific, factual "needle-in-a-haystack" question(s) that require precise details from this page.
These should ask about:
- Specific times, dates, or numbers
- Names of people or organizations
- Exact measurements or quantities
- Specific locations or addresses
- Precise medical findings or technical details

For each question, provide:
1. The question
2. The exact answer (ground truth)
3. A brief hint about where the answer is found (e.g., "mentioned in medical assessment")

Format your response as JSON:
{{
  "questions": [
    {{
      "question": "What time did X occur?",
      "ground_truth_answer": "The exact answer from the text",
      "location_hint": "Where in the page this appears"
    }}
  ]
}}
"""
        
        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that generates test questions for RAG evaluation."},
                    {"role": "user", "content": needle_prompt}
                ],
                temperature=0.3,
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            
            for q in result.get('questions', []):
                questions.append({
                    'question': q['question'],
                    'ground_truth_answer': q['ground_truth_answer'],
                    'query_type': 'needle',
                    'source_page': page_num,
                    'location_hint': q.get('location_hint', ''),
                    'expected_chunks': [f"page_{page_num}_chunk_*"]  # User will refine
                })
        
        except Exception as e:
            print(f"[ERROR] Failed to generate needle questions for page {page_num}: {e}")
    
    # Generate summary questions (high-level)
    if summary_count > 0:
        summary_prompt = f"""You are creating test questions for a RAG system evaluation.

Page {page_num} - {metadata['header']}
Date: {metadata['date']}
Type: {metadata['type']}

Content:
{content}

Generate {summary_count} high-level summary question(s) that require understanding the overall content of this page or multiple pages.
These should ask about:
- Overall outcomes or results
- Key themes or main points
- Relationships between events
- Total costs or aggregated data
- General timelines or sequences

For each question, provide:
1. The question
2. The comprehensive answer (ground truth)
3. A note about what pages might be relevant

Format your response as JSON:
{{
  "questions": [
    {{
      "question": "What was the overall outcome of X?",
      "ground_truth_answer": "A comprehensive answer synthesizing the information",
      "pages_involved": "Page X covers the main points..."
    }}
  ]
}}
"""
        
        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that generates test questions for RAG evaluation."},
                    {"role": "user", "content": summary_prompt}
                ],
                temperature=0.3,
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            
            for q in result.get('questions', []):
                questions.append({
                    'question': q['question'],
                    'ground_truth_answer': q['ground_truth_answer'],
                    'query_type': 'summary',
                    'source_page': page_num,
                    'pages_involved': q.get('pages_involved', ''),
                    'expected_chunks': [f"page_{page_num}_chunk_0"]  # User will refine
                })
        
        except Exception as e:
            print(f"[ERROR] Failed to generate summary questions for page {page_num}: {e}")
    
    return questions


def generate_test_questions(target_needle=5, target_summary=5):
    """
    Generate a balanced set of test questions.
    
    Args:
        target_needle: Target number of needle questions
        target_summary: Target number of summary questions
    
    Returns:
        List of all generated questions
    """
    print("\n" + "=" * 70)
    print("SEMI-AUTOMATIC QUESTION GENERATOR")
    print("=" * 70)
    
    # Initialize OpenAI client
    client = OpenAI(api_key=config.OPENAI_API_KEY)
    
    # Load pages
    pages = load_pdf_pages()
    
    # Strategy: Generate questions from key pages
    # Needle questions: Spread across different detail pages (pages 2-9)
    # Summary questions: Focus on overview pages and key events
    
    all_questions = []
    
    print("\n[STEP 1] Generating needle questions...")
    print("-" * 70)
    
    # Pages with rich specific details for needle questions
    needle_pages = [2, 3, 4, 5, 7]  # Different event pages
    questions_per_page = max(1, target_needle // len(needle_pages))
    
    for page_num in needle_pages:
        page = next((p for p in pages if p['page_number'] == page_num), None)
        if page:
            print(f"  Generating for Page {page_num}: {page['metadata']['header'][:50]}...")
            questions = generate_questions_for_page(page, client, needle_count=questions_per_page)
            all_questions.extend(questions)
            if len([q for q in all_questions if q['query_type'] == 'needle']) >= target_needle:
                break
    
    print(f"\n[OK] Generated {len([q for q in all_questions if q['query_type'] == 'needle'])} needle questions")
    
    print("\n[STEP 2] Generating summary questions...")
    print("-" * 70)
    
    # Pages for summary questions
    summary_pages = [1, 6, 8, 10]  # Overview + key detail pages
    questions_per_page = max(1, target_summary // len(summary_pages))
    
    for page_num in summary_pages:
        page = next((p for p in pages if p['page_number'] == page_num), None)
        if page:
            print(f"  Generating for Page {page_num}: {page['metadata']['header'][:50]}...")
            questions = generate_questions_for_page(page, client, summary_count=questions_per_page)
            all_questions.extend(questions)
            if len([q for q in all_questions if q['query_type'] == 'summary']) >= target_summary:
                break
    
    print(f"\n[OK] Generated {len([q for q in all_questions if q['query_type'] == 'summary'])} summary questions")
    
    return all_questions


def save_suggested_questions(questions, output_file="Evaluation/suggested_questions.json"):
    """Save generated questions to JSON file for review."""
    # Add IDs and format
    formatted_questions = []
    needle_count = 1
    summary_count = 1
    
    for q in questions:
        if q['query_type'] == 'needle':
            q_id = f"needle_{needle_count:02d}"
            needle_count += 1
        else:
            q_id = f"summary_{summary_count:02d}"
            summary_count += 1
        
        formatted_q = {
            "id": q_id,
            "question": q['question'],
            "ground_truth_answer": q['ground_truth_answer'],
            "expected_chunks": q['expected_chunks'],
            "query_type": q['query_type'],
            "source_page": q['source_page'],
            "_note": q.get('location_hint') or q.get('pages_involved', '')
        }
        formatted_questions.append(formatted_q)
    
    output_data = {
        "_instructions": "Review these suggested questions and edit as needed. Update 'expected_chunks' with actual chunk IDs from Supabase. Once reviewed, copy the 'test_cases' to test_dataset.json",
        "test_cases": formatted_questions
    }
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)
    
    print(f"\n[OK] Saved suggested questions to: {output_file}")
    print("\nNext steps:")
    print("  1. Review the suggested_questions.json file")
    print("  2. Edit questions and answers as needed")
    print("  3. Update 'expected_chunks' with actual chunk IDs from Supabase")
    print("  4. Copy the 'test_cases' array to 'test_dataset.json'")


if __name__ == "__main__":
    print("\nGenerating test questions for RAGAS evaluation...")
    
    try:
        questions = generate_test_questions(target_needle=5, target_summary=5)
        
        print("\n" + "=" * 70)
        print(f"GENERATED {len(questions)} QUESTIONS TOTAL")
        print("=" * 70)
        
        save_suggested_questions(questions)
        
        print("\n" + "=" * 70)
        print("Question generation completed successfully!")
        print("=" * 70)
        
    except Exception as e:
        print(f"\n[ERROR] Question generation failed: {e}")
        import traceback
        traceback.print_exc()

