"""
Needle Agent - Handles specific detail queries using hierarchical small chunks

This agent retrieves precise information from small chunks and can auto-merge
with parent context when needed.
"""

import sys
from pathlib import Path
import json
import numpy as np

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from openai import OpenAI
from supabase import create_client
import os
from dotenv import load_dotenv

load_dotenv()

from Config import config


class NeedleAgent:
    """
    Retrieves specific details from small chunks using vector similarity search.
    Performs 'needle in a haystack' queries for precise information.
    Implements auto-merging: retrieves small chunks for precision, then fetches
    parent pages for additional context when needed.
    """
    
    def __init__(self):
        """Initialize the needle agent with OpenAI and Supabase clients."""
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY not found in environment variables")
        
        self.client = OpenAI(api_key=self.api_key)
        self.embedding_model = config.EMBEDDING_MODEL
        self.llm_model = config.SUMMARY_MODEL
        
        # Initialize Supabase client
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_KEY")
        
        if not supabase_url or not supabase_key:
            raise ValueError("Supabase credentials not found in environment variables")
        
        self.supabase = create_client(supabase_url, supabase_key)
        self.chunks_table = config.CHUNKS_TABLE
        
        # Load parent documents from local docstore
        self.parent_docs = self._load_parent_docs()
    
    def _load_parent_docs(self) -> dict:
        """Load parent page documents from local docstore."""
        docstore_path = config.DOCSTORE_PATH
        
        try:
            with open(docstore_path, 'r', encoding='utf-8') as f:
                docstore_data = json.load(f)
            
            # Handle LlamaIndex docstore format: {"docstore/data": {...}, "docstore/metadata": {...}}
            if "docstore/data" in docstore_data:
                parent_dict = docstore_data["docstore/data"]
                print(f"[NEEDLE AGENT] Loaded {len(parent_dict)} parent pages from docstore")
                return parent_dict
            
            # Fallback: treat as list or direct dict
            parent_dict = {}
            docs_list = docstore_data if isinstance(docstore_data, list) else [docstore_data]
            
            for doc in docs_list:
                page_id = doc.get('id_', doc.get('metadata', {}).get('page_id'))
                if page_id:
                    parent_dict[page_id] = doc
            
            print(f"[NEEDLE AGENT] Loaded {len(parent_dict)} parent pages from docstore")
            return parent_dict
            
        except FileNotFoundError:
            print(f"[WARNING] Docstore not found at {docstore_path}")
            return {}
        except Exception as e:
            print(f"[WARNING] Failed to load parent docs: {e}")
            import traceback
            traceback.print_exc()
            return {}
    
    def _get_query_embedding(self, query: str) -> list:
        """Generate embedding for the user's query."""
        response = self.client.embeddings.create(
            model=self.embedding_model,
            input=query
        )
        return response.data[0].embedding
    
    def search_chunks(self, query: str, top_k: int = None) -> list:
        """
        Search for relevant chunks using vector similarity (cosine similarity).
        
        Args:
            query: User's question
            top_k: Number of top results to retrieve (uses config default if None)
            
        Returns:
            list: Top matching chunks ranked by similarity score
        """
        # Use configured value if not specified
        if top_k is None:
            top_k = getattr(config, 'NEEDLE_TOP_K', 4)
        
        print(f"\n[NEEDLE AGENT] Searching for: '{query}'")
        print(f"[NEEDLE AGENT] Computing semantic similarity...")
        
        # Get query embedding
        query_embedding = np.array(self._get_query_embedding(query))
        
        try:
            # Retrieve all chunks with embeddings
            response = self.supabase.table(self.chunks_table).select(
                "chunk_id, content, metadata, page_number, chunk_index, parent_id, embedding"
            ).execute()
            
            chunks = response.data
            
            if not chunks:
                print("[WARNING] No chunks found in database")
                return []
            
            print(f"[NEEDLE AGENT] Found {len(chunks)} total chunks in database")
            
            # Compute cosine similarity for each chunk
            similarities = []
            for chunk in chunks:
                # Convert embedding from list/string to numpy array
                chunk_emb = chunk['embedding']
                if isinstance(chunk_emb, str):
                    # If stored as string, parse it
                    import json
                    chunk_emb = json.loads(chunk_emb) if chunk_emb.startswith('[') else chunk_emb
                chunk_embedding = np.array(chunk_emb, dtype=np.float32)
                
                # Cosine similarity: dot product / (norm1 * norm2)
                similarity = np.dot(query_embedding, chunk_embedding) / (
                    np.linalg.norm(query_embedding) * np.linalg.norm(chunk_embedding)
                )
                
                similarities.append((similarity, chunk))
            
            # Sort by similarity score (highest first)
            similarities.sort(key=lambda x: x[0], reverse=True)
            
            # Return top-k most similar chunks
            top_chunks = [chunk for score, chunk in similarities[:top_k]]
            
            # Log similarity scores for transparency
            print(f"[NEEDLE AGENT] Top {len(top_chunks)} chunks ranked by similarity:")
            for i, (score, chunk) in enumerate(similarities[:top_k], 1):
                page = chunk.get('page_number', '?')
                chunk_index = chunk.get('metadata', {}).get('chunk_index', '?')
                print(f"  {i}. Page {page}, Chunk {chunk_index} (similarity: {score:.4f})")
            
            return top_chunks
            
        except Exception as e:
            print(f"[ERROR] Failed to search chunks: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def _get_parent_context(self, parent_id: str) -> str:
        """
        Retrieve the full parent page content for a chunk.
        
        Args:
            parent_id: The ID of the parent page
            
        Returns:
            str: Full parent page text, or empty string if not found
        """
        if parent_id in self.parent_docs:
            parent_doc = self.parent_docs[parent_id]
            # Handle different docstore formats
            if isinstance(parent_doc, dict):
                # Try different possible text fields
                return parent_doc.get('text', parent_doc.get('__data__', {}).get('text', ''))
            elif isinstance(parent_doc, str):
                return parent_doc
        return ""
    
    def answer_query(self, query: str, top_k: int = None, use_auto_merge: bool = True, merge_threshold: int = None) -> dict:
        """
        Answer a specific detail query using relevant chunks with auto-merging.
        
        Auto-merging logic:
        - If N child chunks from the same parent are retrieved
        - AND N >= merge_threshold
        - THEN replace those chunks with the full parent page
        
        Args:
            query: User's question
            top_k: Number of chunks to retrieve (uses config default if None)
            use_auto_merge: Whether to use auto-merge logic (default True)
            merge_threshold: Number of chunks from same parent needed to trigger merge (default from config)
            
        Returns:
            dict: {"answer": str, "sources": list, "chunks_used": int, "parent_pages_used": int}
        """
        # Use configured values if not specified
        if merge_threshold is None:
            merge_threshold = getattr(config, 'AUTO_MERGE_THRESHOLD', 2)
        if top_k is None:
            top_k = getattr(config, 'NEEDLE_TOP_K', 4)
        
        # Retrieve relevant chunks
        chunks = self.search_chunks(query, top_k)
        
        if not chunks:
            return {
                "answer": "I couldn't find relevant information to answer your question.",
                "sources": [],
                "chunks_used": 0,
                "parent_pages_used": 0
            }
        
        # Count chunks per parent to determine if auto-merge should happen
        parent_chunk_count = {}
        for chunk in chunks:
            metadata = chunk.get('metadata', {})
            parent_id = metadata.get('parent_id', chunk.get('parent_id'))
            if parent_id:
                parent_chunk_count[parent_id] = parent_chunk_count.get(parent_id, 0) + 1
        
        # Determine which parents should be merged (threshold met)
        parents_to_merge = {
            parent_id for parent_id, count in parent_chunk_count.items()
            if count >= merge_threshold
        } if use_auto_merge else set()
        
        if parents_to_merge:
            print(f"[NEEDLE AGENT] Auto-merge threshold met for {len(parents_to_merge)} parent(s): {parents_to_merge}")
            print(f"[NEEDLE AGENT] Threshold: {merge_threshold} chunks from same parent")
        
        # Build context: Keep ALL chunks + ADD parent pages when threshold is met
        context_parts = []
        sources = []
        parents_already_added = set()
        
        # First, add ALL retrieved chunks (precision)
        for i, chunk in enumerate(chunks, 1):
            content = chunk.get('content', '')
            metadata = chunk.get('metadata', {})
            page_num = metadata.get('page_number', chunk.get('page_number', 'Unknown'))
            header = metadata.get('header', 'Unknown')
            chunk_id = chunk.get('chunk_id', f'chunk_{i}')
            
            context_parts.append(f"[Chunk {i} - Page {page_num}: {header}]\n{content}")
            
            # Add each chunk to sources (all chunks, not just one per page)
            sources.append({
                "page": page_num,
                "header": header,
                "chunk_id": chunk_id,
                "content": content,  # Content for RAGAS evaluation
                "metadata": metadata
            })
        
        # Second, ADD parent pages where threshold is met (broader context)
        if parents_to_merge:
            context_parts.append("\n" + "="*70)
            context_parts.append("[ADDITIONAL CONTEXT - Full Parent Pages]")
            context_parts.append("="*70 + "\n")
            
            for chunk in chunks:
                metadata = chunk.get('metadata', {})
                parent_id = metadata.get('parent_id', chunk.get('parent_id'))
                page_num = metadata.get('page_number', chunk.get('page_number', 'Unknown'))
                header = metadata.get('header', 'Unknown')
                
                # Add parent page if threshold met and not yet added
                if parent_id in parents_to_merge and parent_id not in parents_already_added:
                    parent_text = self._get_parent_context(parent_id)
                    if parent_text:
                        context_parts.append(
                            f"[FULL PAGE - Page {page_num}: {header}]\n{parent_text}\n"
                        )
                        parents_already_added.add(parent_id)
                        print(f"[NEEDLE AGENT] Added parent page '{parent_id}' as supplementary context ({parent_chunk_count[parent_id]} chunks from this page)")
        
        context = "\n\n".join(context_parts)
        chunks_used_count = len(chunks)  # All chunks are used
        
        # Generate answer using LLM
        system_prompt = """You are a precise assistant answering questions about an insurance claim.

Your task:
1. Answer the user's question using the provided context from the insurance claim documents
2. Be specific and cite exact details (times, dates, numbers, names) when available
3. If the answer is not in the context, say "The information is not available in the provided documents."
4. Keep answers concise, factual, and professional
5. DO NOT mention "chunks", "pages", or internal document structure in your answer
6. Present information naturally as if reading from a complete document

IMPORTANT: Answer directly and professionally without referencing the document structure."""

        user_prompt = f"""Context from insurance claim:

{context}

Question: {query}

Answer:"""

        try:
            response = self.client.chat.completions.create(
                model=self.llm_model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.1,  # Low temperature for factual accuracy
                max_tokens=500
            )
            
            answer = response.choices[0].message.content.strip()
            
            return {
                "answer": answer,
                "sources": sources,
                "chunks_used": chunks_used_count,
                "parent_pages_used": len(parents_already_added)
            }
            
        except Exception as e:
            print(f"[ERROR] Failed to generate answer: {e}")
            return {
                "answer": "An error occurred while generating the answer.",
                "sources": sources,
                "chunks_used": chunks_used_count,
                "parent_pages_used": len(parents_already_added)
            }


# Example usage and testing
if __name__ == "__main__":
    agent = NeedleAgent()
    
    test_queries = [
        "What time did the collision occur?",
        "What was Sarah Mitchell's blood pressure?",
        "What was the license plate of Chen's vehicle?",
        "How many feet were the skid marks?"
    ]
    
    print("=" * 70)
    print("NEEDLE AGENT TEST")
    print("=" * 70)
    
    for query in test_queries:
        print(f"\n{'='*70}")
        print(f"Query: {query}")
        print('='*70)
        
        result = agent.answer_query(query, top_k=3)
        
        print(f"\nAnswer:\n{result['answer']}")
        print(f"\nChunks used: {result['chunks_used']}")
        print(f"\nSources:")
        for source in result['sources']:
            print(f"  - Page {source['page']}: {source['header']}")

