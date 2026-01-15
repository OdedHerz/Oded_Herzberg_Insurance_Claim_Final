"""
Summary Indexing System
Creates one summary chunk per page and stores in Supabase vector store
"""

import json
from typing import List
from llama_index.core import Document, VectorStoreIndex, StorageContext, Settings
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.llms.openai import OpenAI
from llama_index.readers.file import PyMuPDFReader
from supabase import create_client, Client

# Handle imports for both module execution and direct script execution
from Config import config

# Configure LlamaIndex settings
Settings.llm = OpenAI(model=config.SUMMARY_MODEL, temperature=config.TEMPERATURE, api_key=config.OPENAI_API_KEY)
Settings.embed_model = OpenAIEmbedding(model=config.EMBEDDING_MODEL, api_key=config.OPENAI_API_KEY)


def load_pdf_pages() -> List[Document]:
    """Load PDF pages as separate documents"""
    print("Loading PDF document...")
    
    reader = PyMuPDFReader()
    pdf_documents = reader.load(file_path=config.PDF_PATH)
    
    # Load metadata
    with open(config.METADATA_PATH, 'r', encoding='utf-8') as f:
        metadata_dict = json.load(f)
    
    # Enrich with metadata
    enriched_docs = []
    for i, doc in enumerate(pdf_documents, start=1):
        page_key = f"page_{i}"
        if page_key in metadata_dict:
            meta = metadata_dict[page_key]
            doc.metadata.update({
                "page_number": meta["page_number"],
                "header": meta["header"],
                "involved_parties": ", ".join(meta["involved_parties"]),
                "date": meta["date"],
                "type": meta["type"],
                "page_id": page_key
            })
            enriched_docs.append(doc)
    
    print(f"[OK] Loaded {len(enriched_docs)} pages")
    return enriched_docs


def generate_summary_for_page(page_doc: Document, llm: OpenAI) -> str:
    """Generate a concise summary for a single page"""
    
    page_type = page_doc.metadata.get("type", "page")
    header = page_doc.metadata.get("header", "Unknown")
    
    # Extract common metadata
    page_date = page_doc.metadata.get('date', 'date not specified')
    involved_parties = page_doc.metadata.get('involved_parties', [])
    parties_str = ', '.join(involved_parties) if involved_parties else 'not specified'
    
    if page_type == "Overview":
        prompt = f"""You are analyzing an insurance claim overview page.
        
Page Header: {header}
Claim Date: {page_date}
Involved Parties: {parties_str}
Content: {page_doc.text}

Create a brief summary (75-100 words maximum) that captures:
1. Claim ID and date (use Claim Date: {page_date})
2. Policyholder name and vehicle
3. Incident type, location, and when it occurred
4. Total estimated claim value

Include the specific date. Keep it concise and factual. Summary:"""
    else:
        prompt = f"""You are analyzing an insurance claim detail page.

Page Header: {header}
Event Date: {page_date}
Involved Parties: {parties_str}
Content: {page_doc.text}

Create a brief summary (75-100 words maximum) that captures:
1. When this event occurred (use the Event Date: {page_date})
2. What happened (2-3 key actions)
3. Key people/organizations involved (from the Involved Parties listed above)
4. Most important finding or detail
5. Any costs or financial amounts mentioned

Include the specific date and relevant parties in your summary. Be concise and focus on facts only. Summary:"""
    
    # Generate summary using LLM
    response = llm.complete(prompt)
    summary_text = response.text.strip()
    
    return summary_text


def create_summary_chunks(documents: List[Document]) -> List[Document]:
    """Create summary chunks for each page"""
    print("\nGenerating summaries for each page...")
    
    llm = OpenAI(model=config.SUMMARY_MODEL, temperature=config.TEMPERATURE, api_key=config.OPENAI_API_KEY)
    
    summary_docs = []
    for doc in documents:
        page_id = doc.metadata["page_id"]
        page_num = doc.metadata["page_number"]
        page_type = doc.metadata["type"]
        header = doc.metadata["header"]
        
        print(f"\n  Processing {page_id}: {header}")
        print(f"    Original length: {len(doc.text)} chars")
        
        # Generate summary
        summary_text = generate_summary_for_page(doc, llm)
        print(f"    Summary length: {len(summary_text)} chars")
        
        # Create summary document
        summary_doc = Document(
            text=summary_text,
            metadata={
                "page_number": page_num,
                "summary_id": f"{page_id}_summary",
                "summary_type": page_type,
                "header": header,
                "date": doc.metadata["date"],
                "involved_parties": doc.metadata["involved_parties"],
                "original_length": len(doc.text)
            }
        )
        summary_doc.id_ = summary_doc.metadata["summary_id"]
        
        summary_docs.append(summary_doc)
        print(f"    [OK] Summary created: {summary_doc.id_}")
    
    print(f"\n[OK] Created {len(summary_docs)} summary chunks")
    return summary_docs


def store_summaries_in_supabase(summary_docs: List[Document]) -> VectorStoreIndex:
    """Store summary chunks in Supabase public tables"""
    print("\nStoring summaries in Supabase public table...")
    
    # Initialize Supabase client
    supabase: Client = create_client(config.SUPABASE_URL, config.SUPABASE_KEY)
    
    # Generate embeddings and store summaries
    print(f"Generating embeddings for {len(summary_docs)} summaries...")
    from llama_index.embeddings.openai import OpenAIEmbedding
    embed_model = OpenAIEmbedding(model=config.EMBEDDING_MODEL, api_key=config.OPENAI_API_KEY)
    
    for i, doc in enumerate(summary_docs):
        # Generate embedding
        embedding = embed_model.get_text_embedding(doc.text)
        
        # Prepare data for Supabase
        data = {
            "summary_id": doc.metadata["summary_id"],
            "content": doc.text,
            "embedding": embedding,
            "metadata": doc.metadata,
            "page_number": doc.metadata["page_number"],
            "summary_type": doc.metadata["summary_type"]
        }
        
        # Upsert into Supabase (insert or update if exists based on summary_id)
        try:
            result = supabase.table(config.SUMMARIES_TABLE).upsert(
                data,
                on_conflict="summary_id"  # Update if summary_id already exists
            ).execute()
            print(f"  Stored {i + 1}/{len(summary_docs)} summaries...")
        except Exception as e:
            print(f"\n✗ Error storing summary {i + 1}: {e}")
            print("This usually means the Supabase REST API hasn't recognized the tables yet.")
            print("Please wait 5-10 seconds and try running the indexing again.")
            raise
    
    print(f"[OK] All {len(summary_docs)} summaries stored in Supabase table: {config.SUMMARIES_TABLE}")
    
    # Create vector index from summaries
    storage_context = StorageContext.from_defaults()
    index = VectorStoreIndex.from_documents(
        summary_docs,
        storage_context=storage_context,
        show_progress=False
    )
    
    # Persist index metadata
    index.storage_context.persist(persist_dir=config.SUMMARY_INDEX_PATH)
    print(f"[OK] Summary index metadata saved to: {config.SUMMARY_INDEX_PATH}")
    
    return index


def create_summary_index():
    """Main function to create summary index"""
    print("=" * 70)
    print("SUMMARY INDEXING - High-Level Query System")
    print("=" * 70)
    
    try:
        # Check if claim_summaries table exists before proceeding
        import psycopg2
        import re
        
        match = re.search(r'https://([^.]+)\.supabase\.co', config.SUPABASE_URL)
        if match:
            project_id = match.group(1)
            db_host = f"db.{project_id}.supabase.co"
            
            try:
                conn = psycopg2.connect(
                    host=db_host,
                    port=5432,
                    database="postgres",
                    user="postgres",
                    password=config.SUPABASE_DB_PASSWORD
                )
                cursor = conn.cursor()
                cursor.execute(f"""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables 
                        WHERE table_schema = 'public' AND table_name = '{config.SUMMARIES_TABLE}'
                    );
                """)
                table_exists = cursor.fetchone()[0]
                cursor.close()
                conn.close()
                
                if not table_exists:
                    print(f"\n✗ ERROR: Table '{config.SUMMARIES_TABLE}' does not exist!")
                    print("\nThis table is required for summary indexing.")
                    print("Please run database setup first:")
                    print("  1. From main menu, select option 2 (Create/Recreate Indexing)")
                    print("  2. Or run: python Indexing/create_all_indexes.py")
                    return None
                    
            except Exception as e:
                print(f"\n✗ ERROR: Cannot connect to database: {e}")
                print("\nPlease check your database credentials in .env file")
                return None
        
        # Validate configuration
        config.validate_config()
        
        # Load PDF pages
        documents = load_pdf_pages()
        
        # Generate summaries for each page
        summary_docs = create_summary_chunks(documents)
        
        # Store in Supabase
        index = store_summaries_in_supabase(summary_docs)
        
        print("\n" + "=" * 70)
        print("SUMMARY INDEX CREATION COMPLETE!")
        print("=" * 70)
        print(f"\n=== Summary ===")
        print(f"  • Pages processed: {len(documents)}")
        print(f"  • Summaries created: {len(summary_docs)}")
        print(f"  • Summary model: {config.SUMMARY_MODEL}")
        print(f"  • Embedding model: {config.EMBEDDING_MODEL}")
        print(f"\n=== Files created ===")
        print(f"  • {config.SUMMARY_INDEX_PATH}/ - Vector index metadata")
        print(f"\n=== Supabase ===")
        print(f"  • Table: {config.SUMMARIES_TABLE}")
        print(f"  • Summaries stored with embeddings")
        print("\n[OK] Ready for high-level summarization queries!")
        
        # Print summary examples
        print("\n=== Sample Summaries ===")
        for i, summary_doc in enumerate(summary_docs[:2], 1):
            print(f"\n  {i}. {summary_doc.metadata['header']}")
            print(f"     {summary_doc.text[:150]}...")
        
        return index
        
    except Exception as e:
        print(f"\n[ERROR] Error creating summary index: {e}")
        import traceback
        traceback.print_exc()
        raise


if __name__ == "__main__":
    create_summary_index()

