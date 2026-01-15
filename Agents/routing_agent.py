"""
Routing Agent - Classifies user queries to determine the appropriate retrieval strategy

This agent decides whether a query requires:
- "summary": High-level overview questions (summary chunks)
- "needle": Specific detail questions (hierarchical small chunks)
"""

from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()


class RoutingAgent:
    """
    Routes user queries to the appropriate agent based on query type.
    Uses GPT-4o-mini to classify queries as either 'summary' or 'needle' type.
    """
    
    def __init__(self):
        """Initialize the routing agent with OpenAI client."""
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY not found in environment variables")
        
        self.client = OpenAI(api_key=api_key)
        self.model = "gpt-4o-mini"
        
        # System prompt with clear instructions and examples
        self.system_prompt = """You are a query routing agent for an insurance claim retrieval system.

Your task is to analyze user queries and classify them into ONE of two categories:

1. **SUMMARY** - High-level, broad questions that require an overview or general understanding:
   - Questions about overall timelines, date spans, or duration of processes
   - Questions asking "what happened" in general terms
   - Questions about overall liability, fault determination, or conclusions
   - Questions about total costs, damages, or final outcomes
   - Questions asking for general summaries or overviews
   - Questions about the scope or extent of events ("entire claim", "whole process")
   - Questions with words like: "overall", "summary", "timeline", "sequence of events", "what happened", "entire", "total duration", "date span"

2. **NEEDLE** - Specific, detailed questions looking for precise information:
   - Questions about exact times, dates of specific events, locations, or measurements
   - Questions about specific people, vehicles, or objects (but NOT comprehensive journeys/processes)
   - Questions about specific actions or observations at a particular moment
   - Questions asking for precise numbers, values, or technical details
   - Questions with words like: "exactly", "specifically", "what time", "how many", "who", "which", "where exactly"
   - Examples: "What is Sarah's blood pressure?" (NEEDLE - single fact), but "Describe Sarah's treatment journey" (SUMMARY - comprehensive)

IMPORTANT DISTINCTION FOR DATE/TIME QUESTIONS:
- "What is the date span of the entire claim?" → SUMMARY (overall timeline/scope)
- "When did the collision occur?" → NEEDLE (specific event date)
- "How long did the claim process take?" → SUMMARY (overall duration)
- "What time did the ambulance arrive?" → NEEDLE (specific time)

EXAMPLES:

Query: "What was the total claim value?"
Classification: SUMMARY
Reasoning: Asking for overall financial outcome requiring synthesis of information.

Query: "What time did the collision occur?"
Classification: NEEDLE
Reasoning: Looking for a specific, precise timestamp of a single event.

Query: "What is the date span of the entire claim?"
Classification: SUMMARY
Reasoning: Asking for the overall timeline/scope from start to finish, requires understanding the full process.

Query: "Summarize the events that led to the claim."
Classification: SUMMARY
Reasoning: Explicitly asking for a summary/overview of events.

Query: "What was Sarah Mitchell's heart rate during the medical assessment?"
Classification: NEEDLE
Reasoning: Looking for a specific medical measurement.

Query: "Who was determined to be at fault?"
Classification: SUMMARY
Reasoning: Asking for overall liability conclusion.

Query: "What was the license plate of Chen's vehicle?"
Classification: NEEDLE
Reasoning: Looking for a specific identifying detail.

Query: "Give me an overview of the emergency response."
Classification: SUMMARY
Reasoning: Explicitly asking for an overview/summary.

Query: "How many feet were the skid marks?"
Classification: NEEDLE
Reasoning: Looking for a precise measurement.

Query: "What were the key findings from the investigation?"
Classification: SUMMARY
Reasoning: Asking for synthesized conclusions from multiple sources.

Query: "What medication was prescribed to Sarah Mitchell?"
Classification: NEEDLE
Reasoning: Looking for specific medical treatment details.

Query: "Describe Sarah Mitchell's medical treatment journey."
Classification: SUMMARY
Reasoning: Asking for comprehensive overview of treatment across multiple phases, requires synthesis.

Query: "What was Sarah Mitchell's blood pressure at the scene?"
Classification: NEEDLE
Reasoning: Looking for a single specific measurement at a specific moment.

INSTRUCTIONS:
1. Analyze the user's query carefully
2. Determine if they need a broad overview (SUMMARY) or specific details (NEEDLE)
3. Respond with ONLY one word: either "SUMMARY" or "NEEDLE"
4. Do not provide explanations or additional text
"""
    
    def route(self, query: str) -> str:
        """
        Route a user query to the appropriate agent.
        
        Args:
            query: The user's question
            
        Returns:
            str: Either "summary" or "needle" (lowercase)
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": query}
                ],
                temperature=0.0,  # Deterministic routing
                max_tokens=10
            )
            
            routing_decision = response.choices[0].message.content.strip().upper()
            
            # Validate response
            if routing_decision not in ["SUMMARY", "NEEDLE"]:
                print(f"[WARNING] Unexpected routing decision: {routing_decision}. Defaulting to NEEDLE.")
                return "needle"
            
            result = routing_decision.lower()
            print(f"\n[ROUTING] Query classified as: {result.upper()}")
            return result
            
        except Exception as e:
            print(f"[ERROR] Routing failed: {e}")
            print("[INFO] Defaulting to NEEDLE agent")
            return "needle"
    
    def route_with_explanation(self, query: str) -> dict:
        """
        Route a query and provide explanation (for debugging/testing).
        
        Args:
            query: The user's question
            
        Returns:
            dict: {"route": "summary" or "needle", "query": original query}
        """
        route = self.route(query)
        return {
            "query": query,
            "route": route
        }


# Example usage and testing
if __name__ == "__main__":
    agent = RoutingAgent()
    
    # Test queries
    test_queries = [
        "What was the total claim value?",
        "What time did the collision occur?",
        "Summarize the events that led to the claim.",
        "What was Sarah Mitchell's blood pressure?",
        "Who was at fault?",
        "What was the license plate of the Toyota Camry?",
        "Give me an overview of the medical treatment.",
        "How long were the skid marks?",
    ]
    
    print("=" * 70)
    print("ROUTING AGENT TEST")
    print("=" * 70)
    
    for query in test_queries:
        result = agent.route_with_explanation(query)
        print(f"\nQuery: {result['query']}")
        print(f"Route: {result['route'].upper()}")
        print("-" * 70)

