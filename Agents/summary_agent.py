"""
Summary Agent - Handles high-level queries using page-level summaries

This agent retrieves and synthesizes information from summary chunks for
broad overview questions about the insurance claim.
"""

import sys
from pathlib import Path
import numpy as np

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from openai import OpenAI
from supabase import create_client
import os
from dotenv import load_dotenv

load_dotenv()

from Config import config


class SummaryAgent:
    """
    Retrieves high-level information from summary chunks.
    Handles overview questions requiring synthesis across events.
    """
    
    def __init__(self):
        """Initialize the summary agent with OpenAI and Supabase clients."""
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
        self.summaries_table = config.SUMMARIES_TABLE
    
    def _get_query_embedding(self, query: str) -> list:
        """Generate embedding for the user's query."""
        response = self.client.embeddings.create(
            model=self.embedding_model,
            input=query
        )
        return response.data[0].embedding
    
    def search_summaries(self, query: str, top_k: int = None) -> list:
        """
        Search for relevant summary chunks using vector similarity (cosine similarity).
        ALWAYS includes Overview pages, plus top-k most similar other pages.
        
        Args:
            query: User's question
            top_k: Total number of summaries to retrieve (uses config default if None)
            
        Returns:
            list: Overview summary + top matching summaries ranked by similarity score
        """
        # Use configured value if not specified
        if top_k is None:
            top_k = getattr(config, 'SUMMARY_TOP_K', 4)
        
        print(f"\n[SUMMARY AGENT] Searching for: '{query}'")
        print(f"[SUMMARY AGENT] Computing semantic similarity...")
        
        # Get query embedding
        query_embedding = np.array(self._get_query_embedding(query))
        
        try:
            # Retrieve all summary chunks with embeddings
            response = self.supabase.table(self.summaries_table).select(
                "summary_id, content, metadata, page_number, summary_type, embedding"
            ).execute()
            
            summaries = response.data
            
            if not summaries:
                print("[WARNING] No summaries found in database")
                return []
            
            print(f"[SUMMARY AGENT] Found {len(summaries)} total summaries in database")
            
            # Separate Overview pages from other pages
            overview_summaries = []
            other_summaries = []
            
            for summary in summaries:
                metadata = summary.get('metadata', {})
                # Check both summary_type in metadata and direct summary_type field
                page_type = metadata.get('summary_type', summary.get('summary_type', ''))
                
                if page_type == 'Overview':
                    overview_summaries.append(summary)
                else:
                    other_summaries.append(summary)
            
            print(f"[SUMMARY AGENT] Found {len(overview_summaries)} Overview page(s) (always included)")
            
            # Compute cosine similarity for non-Overview pages
            similarities = []
            for summary in other_summaries:
                # Convert embedding from list/string to numpy array
                summary_emb = summary['embedding']
                if isinstance(summary_emb, str):
                    # If stored as string, parse it
                    import json
                    summary_emb = json.loads(summary_emb) if summary_emb.startswith('[') else summary_emb
                summary_embedding = np.array(summary_emb, dtype=np.float32)
                
                # Cosine similarity: dot product / (norm1 * norm2)
                similarity = np.dot(query_embedding, summary_embedding) / (
                    np.linalg.norm(query_embedding) * np.linalg.norm(summary_embedding)
                )
                
                similarities.append((similarity, summary))
            
            # Sort by similarity score (highest first)
            similarities.sort(key=lambda x: x[0], reverse=True)
            
            # Return Overview + top-k most similar other pages
            # Adjust top_k to account for Overview (if we want total of 4, get top 3 others)
            num_others = min(top_k - len(overview_summaries), len(similarities))
            top_other_summaries = [summary for score, summary in similarities[:num_others]]
            
            final_summaries = overview_summaries + top_other_summaries
            
            # Log what was selected
            print(f"[SUMMARY AGENT] Selected summaries:")
            for overview in overview_summaries:
                page = overview.get('page_number', '?')
                header = overview.get('metadata', {}).get('header', 'Unknown')
                print(f"  - Page {page}: {header} (Overview - always included)")
            
            print(f"[SUMMARY AGENT] Top {num_others} detail pages ranked by similarity:")
            for i, (score, summary) in enumerate(similarities[:num_others], 1):
                page = summary.get('page_number', '?')
                header = summary.get('metadata', {}).get('header', 'Unknown')
                print(f"  {i}. Page {page}: {header} (similarity: {score:.4f})")
            
            return final_summaries
            
        except Exception as e:
            print(f"[ERROR] Failed to search summaries: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def answer_query(self, query: str, top_k: int = None) -> dict:
        """
        Answer a high-level query using relevant summary chunks.
        
        Args:
            query: User's question
            top_k: Number of summaries to retrieve (uses config default if None)
            
        Returns:
            dict: {"answer": str, "sources": list, "summaries_used": int}
        """
        # Use configured value if not specified
        if top_k is None:
            top_k = getattr(config, 'SUMMARY_TOP_K', 4)
        
        # Retrieve relevant summaries
        summaries = self.search_summaries(query, top_k)
        
        if not summaries:
            return {
                "answer": "I couldn't find relevant information to answer your question.",
                "sources": [],
                "summaries_used": 0
            }
        
        # Build context from summaries
        context_parts = []
        sources = []
        
        for summary in summaries:
            content = summary.get('content', '')
            metadata = summary.get('metadata', {})
            page_num = metadata.get('page_number', summary.get('page_number', 'Unknown'))
            header = metadata.get('header', 'Unknown')
            page_type = metadata.get('summary_type', metadata.get('type', 'Unknown'))
            
            context_parts.append(f"[Page {page_num}: {header}]\n{content}")
            sources.append({
                "page": page_num,
                "header": header,
                "summary_id": summary.get('summary_id'),
                "summary": content,  # Add summary content for RAGAS evaluation
                "type": page_type,
                "metadata": metadata
            })
        
        context = "\n\n".join(context_parts)
        
        # Generate answer using LLM
        system_prompt = """You are an assistant providing high-level summaries and overviews of an insurance claim.

Your task:
1. Answer the user's question by synthesizing information from the insurance claim documents
2. Provide CONCISE BUT COMPLETE answers (typically 3-5 sentences)
3. Include key supporting facts, evidence, and relevant details
4. Ensure the answer fully addresses all aspects of the question
5. Be thorough without being redundant or verbose
6. Match the directness of the question - broad questions get brief overviews, specific questions get focused details
7. If the answer requires specific details not available, acknowledge this
8. Keep answers clear, well-organized, and professional
9. DO NOT mention "pages", "summaries", or internal document structure
10. Present information naturally as a cohesive narrative

Format your response with clear structure. Be comprehensive but concise."""

        user_prompt = f"""Insurance claim summaries:

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
                temperature=0.3,  # Slightly higher for better synthesis
                max_tokens=700  # Balanced for complete answers with key details
            )
            
            answer = response.choices[0].message.content.strip()
            
            return {
                "answer": answer,
                "sources": sources,
                "summaries_used": len(summaries)
            }
            
        except Exception as e:
            print(f"[ERROR] Failed to generate answer: {e}")
            return {
                "answer": "An error occurred while generating the answer.",
                "sources": sources,
                "summaries_used": len(summaries)
            }


# Example usage and testing
if __name__ == "__main__":
    agent = SummaryAgent()
    
    test_queries = [
        "What was the total claim value?",
        "Summarize the events that led to the claim.",
        "Who was at fault and why?",
        "Give me an overview of the medical treatment."
    ]
    
    print("=" * 70)
    print("SUMMARY AGENT TEST")
    print("=" * 70)
    
    for query in test_queries:
        print(f"\n{'='*70}")
        print(f"Query: {query}")
        print('='*70)
        
        result = agent.answer_query(query)
        
        print(f"\nAnswer:\n{result['answer']}")
        print(f"\nSummaries used: {result['summaries_used']}")
        print(f"\nSources:")
        for source in result['sources']:
            print(f"  - Page {source['page']}: {source['header']}")

