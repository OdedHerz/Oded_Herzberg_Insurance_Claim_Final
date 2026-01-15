"""
RAGAS Evaluation Runner

This module runs comprehensive RAGAS evaluation on the RAG system using
Gemini as the LLM judge for all metrics.
"""

import json
import os
import sys
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from Config import config
from Agents.routing_agent import RoutingAgent
from Agents.needle_agent import NeedleAgent
from Agents.summary_agent import SummaryAgent

# RAGAS imports
from datasets import Dataset
from ragas import evaluate
from ragas.metrics import (
    context_precision,
    context_recall,
    faithfulness,
    answer_relevancy,
    answer_similarity,
    answer_correctness
)
from langchain_google_genai import ChatGoogleGenerativeAI

# PDF generation
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT


class RAGASEvaluator:
    """Handles RAGAS evaluation of the RAG system."""
    
    def __init__(self):
        """Initialize agents and Gemini judge."""
        print("[EVALUATOR] Initializing evaluation system...")
        
        # Initialize agents
        self.routing_agent = RoutingAgent()
        self.needle_agent = NeedleAgent()
        self.summary_agent = SummaryAgent()
        print("[EVALUATOR] - Agents initialized")
        
        # Initialize Gemini judge
        self.gemini_judge = self._setup_gemini_judge()
        print("[EVALUATOR] - Gemini judge ready")
        
        print("[EVALUATOR] All components initialized!\n")
    
    def _setup_gemini_judge(self) -> ChatGoogleGenerativeAI:
        """Setup Gemini as the evaluator LLM."""
        if not config.GOOGLE_AI_API_KEY:
            raise ValueError(
                "GOOGLE_AI_API_KEY not found in environment variables. "
                "Please add it to your .env file for RAGAS evaluation."
            )
        
        return ChatGoogleGenerativeAI(
            model=config.GEMINI_MODEL,
            google_api_key=config.GOOGLE_AI_API_KEY,
            temperature=0.0,
            convert_system_message_to_human=True,
            max_output_tokens=2048,
            n=1  # Explicitly request 1 generation to avoid warnings
        )
    
    def load_test_dataset(self, dataset_path: str = "Evaluation/test_dataset.json") -> List[Dict[str, Any]]:
        """Load test dataset from JSON file."""
        print(f"[EVALUATOR] Loading test dataset from: {dataset_path}")
        
        try:
            with open(dataset_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            test_cases = data.get('test_cases', [])
            
            needle_count = sum(1 for tc in test_cases if tc['query_type'] == 'needle')
            summary_count = sum(1 for tc in test_cases if tc['query_type'] == 'summary')
            
            print(f"[EVALUATOR] Loaded {len(test_cases)} test cases ({needle_count} needle, {summary_count} summary)\n")
            
            return test_cases
        
        except FileNotFoundError:
            raise FileNotFoundError(
                f"Test dataset not found at {dataset_path}. "
                "Please run 'python Evaluation/question_generator.py' first and review the questions."
            )
        except Exception as e:
            raise Exception(f"Failed to load test dataset: {e}")
    
    def run_single_query(self, test_case: Dict[str, Any], test_num: int, total_tests: int) -> Dict[str, Any]:
        """
        Execute a single test query and capture all data for evaluation.
        
        Args:
            test_case: Test case dictionary with question, ground truth, etc.
            test_num: Current test number
            total_tests: Total number of tests
        
        Returns:
            Dictionary with all evaluation data
        """
        test_id = test_case['id']
        question = test_case['question']
        query_type = test_case['query_type']
        
        print("=" * 70)
        print(f"[TEST {test_num}/{total_tests}] {test_id}")
        print("=" * 70)
        print(f"Question: {question}")
        print(f"Expected Type: {query_type.upper()}")
        print()
        
        # Route the query
        routed_type = self.routing_agent.route(question)
        print(f"[ROUTING] Query routed to: {routed_type.upper()}")
        
        if routed_type != query_type:
            print(f"  [WARNING] Routing mismatch! Expected {query_type}, got {routed_type}")
        
        print()
        
        # Execute appropriate agent and capture detailed data
        if routed_type == "needle":
            result = self._run_needle_query(question)
        else:  # summary
            result = self._run_summary_query(question)
        
        # Print generated answer
        print(f"\n[GENERATED ANSWER]")
        print(f"{result['answer']}")
        print()
        
        # Prepare data for RAGAS
        eval_data = {
            'test_id': test_id,
            'question': question,
            'answer': result['answer'],
            'contexts': result['contexts'],  # List of context strings
            'ground_truth': test_case['ground_truth_answer'],
            'query_type': query_type,
            'routed_type': routed_type,
            'expected_chunks': test_case.get('expected_chunks', []),
            'retrieved_chunk_ids': result['chunk_ids']
        }
        
        return eval_data
    
    def _run_needle_query(self, question: str) -> Dict[str, Any]:
        """Run needle query and capture detailed context."""
        # Get the answer
        result = self.needle_agent.answer_query(question)
        
        # Print retrieved chunks for visibility
        print(f"\n[NEEDLE AGENT] Retrieved {len(result['sources'])} chunks:")
        for i, source in enumerate(result['sources'], 1):
            chunk_id = source.get('chunk_id', 'unknown')
            page = source.get('page', '?')
            # Extract chunk index from chunk_id (format: page_X_chunk_Y)
            chunk_index = chunk_id.split('_')[-1] if '_' in chunk_id else '?'
            print(f"  {i}. {chunk_id} (Page {page}, Chunk {chunk_index})")
        
        # Extract contexts (chunk contents)
        contexts = []
        chunk_ids = []
        
        for source in result['sources']:
            chunk_id = source.get('chunk_id', 'unknown')
            content = source.get('content', '')
            chunk_ids.append(chunk_id)
            contexts.append(content)
        
        return {
            'answer': result['answer'],
            'contexts': contexts,
            'chunk_ids': chunk_ids
        }
    
    def _run_summary_query(self, question: str) -> Dict[str, Any]:
        """Run summary query and capture detailed context."""
        # Get the answer
        result = self.summary_agent.answer_query(question)
        
        # Print retrieved summaries for visibility
        print(f"\n[SUMMARY AGENT] Retrieved {len(result['sources'])} page summaries:")
        for i, source in enumerate(result['sources'], 1):
            page = source.get('page', '?')
            header = source.get('header', 'Unknown')
            page_type = source.get('type', 'Unknown')
            print(f"  {i}. Page {page}: {header} ({page_type})")
        
        # Extract contexts (summary contents)
        contexts = []
        chunk_ids = []
        
        for source in result['sources']:
            page_num = source.get('page', 'unknown')
            content = source.get('summary', '')
            chunk_id = f"page_{page_num}_summary"
            chunk_ids.append(chunk_id)
            contexts.append(content)
        
        return {
            'answer': result['answer'],
            'contexts': contexts,
            'chunk_ids': chunk_ids
        }
    
    def evaluate_with_ragas(self, eval_data_list: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Run RAGAS evaluation using Gemini as the judge.
        
        Args:
            eval_data_list: List of evaluation data dictionaries
        
        Returns:
            RAGAS evaluation results
        """
        print("\n" + "=" * 70)
        print("RUNNING RAGAS METRICS WITH GEMINI JUDGE")
        print("=" * 70)
        
        # Prepare dataset for RAGAS
        ragas_data = {
            'question': [],
            'answer': [],
            'contexts': [],
            'ground_truth': []
        }
        
        for eval_data in eval_data_list:
            ragas_data['question'].append(eval_data['question'])
            ragas_data['answer'].append(eval_data['answer'])
            ragas_data['contexts'].append(eval_data['contexts'])
            ragas_data['ground_truth'].append(eval_data['ground_truth'])
        
        # Create RAGAS dataset
        dataset = Dataset.from_dict(ragas_data)
        
        # Define metrics with Gemini as judge
        metrics = [
            context_precision,
            context_recall,
            faithfulness,
            answer_relevancy,
            answer_similarity,
            answer_correctness
        ]
        
        print("\n[GEMINI JUDGE] Evaluating all test cases across 6 metrics...")
        print("  - Context Precision")
        print("  - Context Recall")
        print("  - Faithfulness")
        print("  - Answer Relevancy")
        print("  - Answer Similarity")
        print("  - Answer Correctness")
        print("\nThis may take a few minutes...\n")
        
        # Run evaluation
        try:
            results = evaluate(
                dataset,
                metrics=metrics,
                llm=self.gemini_judge,
                embeddings=None,  # Will use default
                raise_exceptions=False  # Don't fail on warnings
            )
            
            print("[OK] RAGAS evaluation completed!")
            return results
        
        except Exception as e:
            print(f"[ERROR] RAGAS evaluation failed: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def print_detailed_results(self, eval_data_list: List[Dict[str, Any]], ragas_results: Any):
        """Print detailed results with scoring."""
        print("\n" + "=" * 70)
        print("DETAILED RESULTS BY TEST CASE")
        print("=" * 70)
        
        # Convert results to dict for easier access
        results_df = ragas_results.to_pandas()
        
        for idx, eval_data in enumerate(eval_data_list):
            print(f"\n[{eval_data['test_id']}] {eval_data['question']}")
            print("-" * 70)
            
            # Get scores for this test case
            row = results_df.iloc[idx]
            
            scores = {
                'Context Precision': row.get('context_precision', 0),
                'Context Recall': row.get('context_recall', 0),
                'Faithfulness': row.get('faithfulness', 0),
                'Answer Relevancy': row.get('answer_relevancy', 0),
                'Answer Similarity': row.get('answer_similarity', 0),
                'Answer Correctness': row.get('answer_correctness', 0)
            }
            
            # Print scores with warnings for low scores
            for metric, score in scores.items():
                warning = " [WARNING]" if score < 0.7 else ""
                print(f"  {metric}: {score:.3f}{warning}")
            
            # Check if expected chunks were retrieved
            expected = set(eval_data.get('expected_chunks', []))
            retrieved = set(eval_data.get('retrieved_chunk_ids', []))
            
            # Handle wildcards in expected chunks
            actual_expected = set()
            for exp in expected:
                if exp.endswith('_*'):
                    # Match any chunk from that page
                    prefix = exp[:-1]
                    actual_expected.update([r for r in retrieved if r.startswith(prefix)])
                else:
                    actual_expected.add(exp)
            
            if actual_expected and not actual_expected.intersection(retrieved):
                print(f"  [INFO] Expected chunks: {', '.join(expected)}")
                print(f"  [INFO] Retrieved chunks: {', '.join(retrieved)}")
                print(f"  [WARNING] None of the expected chunks were retrieved!")
        
        # Print aggregate scores
        print("\n" + "=" * 70)
        print("AGGREGATE SCORES")
        print("=" * 70)
        
        avg_scores = {
            'Context Precision': results_df['context_precision'].mean(),
            'Context Recall': results_df['context_recall'].mean(),
            'Faithfulness': results_df['faithfulness'].mean(),
            'Answer Relevancy': results_df['answer_relevancy'].mean(),
            'Answer Similarity': results_df['answer_similarity'].mean(),
            'Answer Correctness': results_df['answer_correctness'].mean()
        }
        
        for metric, score in avg_scores.items():
            warning = " [WARNING]" if score < 0.7 else ""
            print(f"  Average {metric}: {score:.3f}{warning}")
        
        # Overall score
        overall = sum(avg_scores.values()) / len(avg_scores)
        print(f"\n  Overall Score: {overall:.3f}")
    
    def save_results(self, eval_data_list: List[Dict[str, Any]], ragas_results: Any, output_path: str = None):
        """Save evaluation results to JSON file."""
        if output_path is None:
            output_path = config.EVALUATION_RESULTS_PATH
        
        # Convert results to dict
        results_df = ragas_results.to_pandas()
        
        # Load query_results to get its timestamp for reference
        query_results_timestamp = None
        try:
            with open(config.QUERY_RESULTS_PATH, 'r', encoding='utf-8') as f:
                query_data = json.load(f)
                query_results_timestamp = query_data.get('timestamp', 'unknown')
        except Exception as e:
            print(f"[WARNING] Could not load query_results timestamp: {e}")
        
        # Helper function to safely convert values, replacing NaN with None
        import math
        def safe_float(value, default=None):
            if value is None or (isinstance(value, float) and math.isnan(value)):
                return default
            return float(value)
        
        output_data = {
            'evaluation_timestamp': datetime.now().isoformat(),
            'query_results_timestamp': query_results_timestamp,
            'query_results_file': config.QUERY_RESULTS_PATH,
            'total_tests': len(eval_data_list),
            'test_results': [],
            'aggregate_scores': {
                'context_precision': safe_float(results_df['context_precision'].mean()),
                'context_recall': safe_float(results_df['context_recall'].mean()),
                'faithfulness': safe_float(results_df['faithfulness'].mean()),
                'answer_relevancy': safe_float(results_df['answer_relevancy'].mean()),
                'answer_similarity': safe_float(results_df['answer_similarity'].mean()),
                'answer_correctness': safe_float(results_df['answer_correctness'].mean())
            }
        }
        
        # Add individual test results
        for idx, eval_data in enumerate(eval_data_list):
            row = results_df.iloc[idx]
            
            # Helper function already defined above
            def safe_float_local(value, default=None):
                if value is None or (isinstance(value, float) and math.isnan(value)):
                    return default
                return float(value)
            
            test_result = {
                'test_id': eval_data['test_id'],
                'question': eval_data['question'],
                'query_type': eval_data['query_type'],
                'routed_type': eval_data['routed_type'],
                'answer': eval_data['answer'],
                'ground_truth': eval_data['ground_truth'],
                'expected_chunks': eval_data['expected_chunks'],
                'retrieved_chunk_ids': eval_data['retrieved_chunk_ids'],
                'scores': {
                    'context_precision': safe_float_local(row.get('context_precision')),
                    'context_recall': safe_float_local(row.get('context_recall')),
                    'faithfulness': safe_float_local(row.get('faithfulness')),
                    'answer_relevancy': safe_float_local(row.get('answer_relevancy')),
                    'answer_similarity': safe_float_local(row.get('answer_similarity')),
                    'answer_correctness': safe_float_local(row.get('answer_correctness'))
                }
            }
            output_data['test_results'].append(test_result)
        
        # Save to file
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
        
        print(f"[OK] Results saved to: {output_path}")
        print(f"[INFO] Linked to query results: {query_results_timestamp}")
    
    def generate_pdf_report(self, eval_data_list: List[Dict[str, Any]], ragas_results: Any, output_path: str = None, evaluation_timestamp: str = None):
        """
        Generate a comprehensive PDF report of evaluation results.
        
        Args:
            eval_data_list: List of evaluation data dictionaries
            ragas_results: RAGAS results object with metrics
            output_path: Path to save PDF (uses config default if None)
            evaluation_timestamp: ISO timestamp of when evaluation was run (if None, loads from results file)
        """
        if output_path is None:
            output_path = config.EVALUATION_REPORT_PATH
        
        # Get evaluation timestamp from results file if not provided
        if evaluation_timestamp is None:
            try:
                with open(config.EVALUATION_RESULTS_PATH, 'r', encoding='utf-8') as f:
                    results_data = json.load(f)
                    evaluation_timestamp = results_data.get('evaluation_timestamp')
            except Exception as e:
                print(f"[WARNING] Could not load evaluation timestamp: {e}")
                evaluation_timestamp = datetime.now().isoformat()
        
        # Parse and format the timestamp
        try:
            eval_datetime = datetime.fromisoformat(evaluation_timestamp)
            formatted_date = eval_datetime.strftime('%B %d, %Y at %H:%M:%S')
        except Exception:
            formatted_date = evaluation_timestamp  # Use as-is if parsing fails
        
        print(f"\n[PDF REPORT] Generating PDF report...")
        
        # Create PDF
        doc = SimpleDocTemplate(output_path, pagesize=letter,
                              rightMargin=0.5*inch, leftMargin=0.5*inch,
                              topMargin=0.5*inch, bottomMargin=0.5*inch)
        
        # Container for PDF elements
        story = []
        
        # Styles
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1f4788'),
            spaceAfter=30,
            alignment=TA_CENTER
        )
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#1f4788'),
            spaceAfter=12,
            spaceBefore=12
        )
        normal_style = styles['Normal']
        
        # Convert results to DataFrame
        results_df = ragas_results.to_pandas()
        
        # Separate results by query type
        needle_indices = [i for i, e in enumerate(eval_data_list) if e['query_type'] == 'needle']
        summary_indices = [i for i, e in enumerate(eval_data_list) if e['query_type'] == 'summary']
        
        needle_results = results_df.iloc[needle_indices] if needle_indices else None
        summary_results = results_df.iloc[summary_indices] if summary_indices else None
        
        # Calculate aggregate scores for each agent
        metric_names = ['context_precision', 'context_recall', 'faithfulness', 
                       'answer_relevancy', 'answer_similarity', 'answer_correctness']
        
        import math
        import numpy as np
        
        needle_scores = {}
        summary_scores = {}
        overall_scores = {}
        
        for metric in metric_names:
            if needle_results is not None and len(needle_results) > 0:
                needle_scores[metric] = needle_results[metric].mean()
            if summary_results is not None and len(summary_results) > 0:
                summary_scores[metric] = summary_results[metric].mean()
            overall_scores[metric] = results_df[metric].mean()
        
        # Calculate overall averages, excluding NaN values
        def calc_avg_excluding_nan(scores_dict):
            valid_scores = [v for v in scores_dict.values() if not (isinstance(v, float) and math.isnan(v))]
            return sum(valid_scores) / len(valid_scores) if valid_scores else 0
        
        needle_avg = calc_avg_excluding_nan(needle_scores) if needle_scores else 0
        summary_avg = calc_avg_excluding_nan(summary_scores) if summary_scores else 0
        system_avg = calc_avg_excluding_nan(overall_scores)
        
        # OVERVIEW PAGE 1
        story.append(Paragraph("RAGAS Evaluation Report", title_style))
        story.append(Spacer(1, 0.2*inch))
        
        # Metadata
        metadata_text = f"""
        <b>Evaluation Date:</b> {formatted_date}<br/>
        <b>Total Test Cases:</b> {len(eval_data_list)}<br/>
        <b>Needle Questions:</b> {len(needle_indices)}<br/>
        <b>Summary Questions:</b> {len(summary_indices)}<br/>
        <b>Judge Model:</b> {config.GEMINI_MODEL}
        """
        story.append(Paragraph(metadata_text, normal_style))
        story.append(Spacer(1, 0.3*inch))
        
        # OVERALL SYSTEM PERFORMANCE
        story.append(Paragraph("Overall System Performance", heading_style))
        system_color = colors.green if system_avg >= 0.8 else colors.orange if system_avg >= 0.6 else colors.red
        system_text = f'<font color="{system_color.hexval()}"><b>System Score: {system_avg:.3f}</b></font>'
        story.append(Paragraph(system_text, ParagraphStyle('SystemScore', parent=normal_style, fontSize=16, spaceAfter=6)))
        
        # System status
        if system_avg >= 0.8:
            status_text = "✓ Excellent - System performing at high quality"
        elif system_avg >= 0.7:
            status_text = "○ Good - System performing well with room for improvement"
        elif system_avg >= 0.6:
            status_text = "⚠ Acceptable - System needs optimization"
        else:
            status_text = "✗ Poor - System requires significant improvements"
        story.append(Paragraph(status_text, normal_style))
        story.append(Spacer(1, 0.3*inch))
        
        # System-wide metrics table
        story.append(Paragraph("System-Wide Metrics", ParagraphStyle('SubHeading', parent=heading_style, fontSize=14)))
        system_data = [['Metric', 'Score', 'Status']]
        metric_labels = {
            'context_precision': 'Context Precision',
            'context_recall': 'Context Recall',
            'faithfulness': 'Faithfulness',
            'answer_relevancy': 'Answer Relevancy',
            'answer_similarity': 'Answer Similarity',
            'answer_correctness': 'Answer Correctness'
        }
        
        # Helper function to format scores, showing "N/A" for NaN
        def format_score(score):
            if score is None or (isinstance(score, float) and math.isnan(score)):
                return "N/A"
            return f'{score:.3f}'
        
        for metric, score in overall_scores.items():
            label = metric_labels[metric]
            if score is None or (isinstance(score, float) and math.isnan(score)):
                status = '⚠ N/A'
                score_text = "N/A"
            else:
                status = '✓ Excellent' if score >= 0.8 else '○ Good' if score >= 0.7 else '⚠ Needs Work'
                score_text = f'{score:.3f}'
            system_data.append([label, score_text, status])
        
        system_table = Table(system_data, colWidths=[3*inch, 1*inch, 2*inch])
        system_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f4788')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        story.append(system_table)
        story.append(Spacer(1, 0.3*inch))
        
        # Page break to agent-specific performance
        story.append(PageBreak())
        
        # OVERVIEW PAGE 2: AGENT-SPECIFIC PERFORMANCE
        story.append(Paragraph("Agent-Specific Performance", title_style))
        story.append(Spacer(1, 0.2*inch))
        
        # NEEDLE AGENT PERFORMANCE
        if needle_scores:
            story.append(Paragraph("Needle Agent Performance", heading_style))
            story.append(Paragraph(f"<i>Handles specific detail queries (needle-in-a-haystack)</i>", 
                                  ParagraphStyle('Italic', parent=normal_style, fontSize=10, textColor=colors.grey)))
            story.append(Spacer(1, 0.1*inch))
            
            needle_color = colors.green if needle_avg >= 0.8 else colors.orange if needle_avg >= 0.6 else colors.red
            needle_text = f'<font color="{needle_color.hexval()}"><b>Needle Agent Score: {needle_avg:.3f}</b></font> ({len(needle_indices)} tests)'
            story.append(Paragraph(needle_text, ParagraphStyle('NeedleScore', parent=normal_style, fontSize=14, spaceAfter=6)))
            story.append(Spacer(1, 0.1*inch))
            
            # Needle metrics table
            needle_data = [['Metric', 'Score', 'vs System Avg']]
            for metric, score in needle_scores.items():
                label = metric_labels[metric]
                system_score = overall_scores[metric]
                
                # Handle NaN in scores
                if score is None or (isinstance(score, float) and math.isnan(score)):
                    needle_data.append([label, "N/A", "N/A"])
                    continue
                
                if system_score is None or (isinstance(system_score, float) and math.isnan(system_score)):
                    needle_data.append([label, f'{score:.3f}', "N/A"])
                    continue
                    
                diff = score - system_score
                if diff > 0.01:
                    diff_text = Paragraph(f'<font color="green">+{diff:.3f}</font>', normal_style)
                elif diff < -0.05:
                    diff_text = Paragraph(f'<font color="red">{diff:.3f}</font>', normal_style)
                else:
                    diff_text = f'{diff:.3f}'
                needle_data.append([label, f'{score:.3f}', diff_text])
            
            needle_table = Table(needle_data, colWidths=[3*inch, 1*inch, 1.5*inch])
            needle_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2e7d32')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 11),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#c8e6c9')),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ]))
            story.append(needle_table)
            story.append(Spacer(1, 0.3*inch))
        
        # SUMMARY AGENT PERFORMANCE
        if summary_scores:
            story.append(Paragraph("Summary Agent Performance", heading_style))
            story.append(Paragraph(f"<i>Handles high-level overview queries</i>", 
                                  ParagraphStyle('Italic', parent=normal_style, fontSize=10, textColor=colors.grey)))
            story.append(Spacer(1, 0.1*inch))
            
            summary_color = colors.green if summary_avg >= 0.8 else colors.orange if summary_avg >= 0.6 else colors.red
            summary_text = f'<font color="{summary_color.hexval()}"><b>Summary Agent Score: {summary_avg:.3f}</b></font> ({len(summary_indices)} tests)'
            story.append(Paragraph(summary_text, ParagraphStyle('SummaryScore', parent=normal_style, fontSize=14, spaceAfter=6)))
            story.append(Spacer(1, 0.1*inch))
            
            # Summary metrics table
            summary_data = [['Metric', 'Score', 'vs System Avg']]
            for metric, score in summary_scores.items():
                label = metric_labels[metric]
                system_score = overall_scores[metric]
                
                # Handle NaN in scores
                if score is None or (isinstance(score, float) and math.isnan(score)):
                    summary_data.append([label, "N/A", "N/A"])
                    continue
                
                if system_score is None or (isinstance(system_score, float) and math.isnan(system_score)):
                    summary_data.append([label, f'{score:.3f}', "N/A"])
                    continue
                
                diff = score - system_score
                if diff > 0.01:
                    diff_text = Paragraph(f'<font color="green">+{diff:.3f}</font>', normal_style)
                elif diff < -0.05:
                    diff_text = Paragraph(f'<font color="red">{diff:.3f}</font>', normal_style)
                else:
                    diff_text = f'{diff:.3f}'
                summary_data.append([label, f'{score:.3f}', diff_text])
            
            summary_table = Table(summary_data, colWidths=[3*inch, 1*inch, 1.5*inch])
            summary_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1565c0')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 11),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#bbdefb')),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ]))
            story.append(summary_table)
            story.append(Spacer(1, 0.3*inch))
        
        # COMPARATIVE ANALYSIS
        if needle_scores and summary_scores:
            story.append(Paragraph("Comparative Analysis", heading_style))
            
            # Agent comparison table
            comparison_data = [['Agent', 'Avg Score', 'Best Metric', 'Weakest Metric']]
            
            # Needle agent best/worst
            needle_best = max(needle_scores.items(), key=lambda x: x[1])
            needle_worst = min(needle_scores.items(), key=lambda x: x[1])
            comparison_data.append([
                'Needle Agent',
                f'{needle_avg:.3f}',
                f'{metric_labels[needle_best[0]]}: {needle_best[1]:.3f}',
                f'{metric_labels[needle_worst[0]]}: {needle_worst[1]:.3f}'
            ])
            
            # Summary agent best/worst
            summary_best = max(summary_scores.items(), key=lambda x: x[1])
            summary_worst = min(summary_scores.items(), key=lambda x: x[1])
            comparison_data.append([
                'Summary Agent',
                f'{summary_avg:.3f}',
                f'{metric_labels[summary_best[0]]}: {summary_best[1]:.3f}',
                f'{metric_labels[summary_worst[0]]}: {summary_worst[1]:.3f}'
            ])
            
            comparison_table = Table(comparison_data, colWidths=[1.5*inch, 1*inch, 2*inch, 2*inch])
            comparison_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('ALIGN', (1, 0), (1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.lightgrey),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ]))
            story.append(comparison_table)
        
        # Page break before detailed results
        story.append(PageBreak())
        
        # DETAILED RESULTS PAGES
        story.append(Paragraph("Detailed Test Results", title_style))
        story.append(Spacer(1, 0.2*inch))
        
        for idx, eval_data in enumerate(eval_data_list):
            row = results_df.iloc[idx]
            
            # Test header
            story.append(Paragraph(f"Test {idx+1}: {eval_data['test_id']}", heading_style))
            
            # Question
            story.append(Paragraph(f"<b>Question:</b> {eval_data['question']}", normal_style))
            story.append(Spacer(1, 0.1*inch))
            
            # Query type and routing
            story.append(Paragraph(f"<b>Type:</b> {eval_data['query_type'].upper()} (routed to: {eval_data['routed_type'].upper()})", normal_style))
            story.append(Spacer(1, 0.1*inch))
            
            # Ground truth - show full text
            story.append(Paragraph(f"<b>Ground Truth:</b> {eval_data['ground_truth']}", normal_style))
            story.append(Spacer(1, 0.1*inch))
            
            # Agent answer - show full text
            story.append(Paragraph(f"<b>Agent Answer:</b> {eval_data['answer']}", normal_style))
            story.append(Spacer(1, 0.15*inch))
            
            # Scores table
            test_scores_data = [['Metric', 'Score']]
            
            # Helper to format score with NaN check
            def format_test_score(value):
                if value is None or (isinstance(value, float) and math.isnan(value)):
                    return "N/A"
                return f"{value:.3f}"
            
            test_scores_data.append(['Context Precision', format_test_score(row.get('context_precision'))])
            test_scores_data.append(['Context Recall', format_test_score(row.get('context_recall'))])
            test_scores_data.append(['Faithfulness', format_test_score(row.get('faithfulness'))])
            test_scores_data.append(['Answer Relevancy', format_test_score(row.get('answer_relevancy'))])
            test_scores_data.append(['Answer Similarity', format_test_score(row.get('answer_similarity'))])
            test_scores_data.append(['Answer Correctness', format_test_score(row.get('answer_correctness'))])
            
            test_table = Table(test_scores_data, colWidths=[3*inch, 1.5*inch])
            test_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('BACKGROUND', (0, 1), (-1, -1), colors.lightgrey),
            ]))
            story.append(test_table)
            story.append(Spacer(1, 0.15*inch))
            
            # Retrieved chunks - show all
            chunks_text = f"<b>Retrieved:</b> {', '.join(eval_data['retrieved_chunk_ids'])}"
            story.append(Paragraph(chunks_text, ParagraphStyle('Small', parent=normal_style, fontSize=9)))
            
            # Expected chunks
            expected_text = f"<b>Expected:</b> {', '.join(eval_data['expected_chunks'])}"
            story.append(Paragraph(expected_text, ParagraphStyle('Small', parent=normal_style, fontSize=9)))
            
            # Add spacing between tests
            if idx < len(eval_data_list) - 1:
                story.append(Spacer(1, 0.2*inch))
                # Subtle separator with lighter color
                separator_style = ParagraphStyle('Separator', parent=normal_style, 
                                                fontSize=8, textColor=colors.lightgrey)
                story.append(Paragraph("─" * 40, separator_style))
                story.append(Spacer(1, 0.15*inch))
        
        # Build PDF
        doc.build(story)
        
        print(f"[OK] PDF report saved to: {output_path}")
        return output_path


def run_query_phase():
    """
    Phase 1: Run test queries through agents and save results.
    This phase is expensive (runs through OpenAI agents) but only needs to run once.
    """
    print("\n" + "=" * 70)
    print("PHASE 1: QUERY COLLECTION")
    print("=" * 70)
    print("\nThis will:")
    print("  1. Load test dataset")
    print("  2. Run each query through your RAG system")
    print("  3. Capture answers and retrieved contexts")
    print("  4. Save results to query_results.json")
    print("\nEstimated time: 2-3 minutes")
    print("=" * 70)
    
    try:
        # Initialize evaluator (without Gemini judge yet)
        print("\n[PHASE 1] Initializing agents...")
        evaluator = RAGASEvaluator()
        
        # Load test dataset
        test_cases = evaluator.load_test_dataset()
        
        # Run all queries and collect data
        print("\n[PHASE 1] Running queries through agents...")
        eval_data_list = []
        
        for idx, test_case in enumerate(test_cases, 1):
            eval_data = evaluator.run_single_query(test_case, idx, len(test_cases))
            eval_data_list.append(eval_data)
        
        # Save query results to JSON
        output_path = "Evaluation/query_results.json"
        output_data = {
            'timestamp': datetime.now().isoformat(),
            'total_queries': len(eval_data_list),
            'test_cases': []
        }
        
        for eval_data in eval_data_list:
            test_result = {
                'test_id': eval_data['test_id'],
                'question': eval_data['question'],
                'query_type': eval_data['query_type'],
                'routed_type': eval_data['routed_type'],
                'answer': eval_data['answer'],
                'contexts': eval_data['contexts'],
                'retrieved_chunk_ids': eval_data['retrieved_chunk_ids'],
                'ground_truth': eval_data['ground_truth'],
                'expected_chunks': eval_data['expected_chunks']
            }
            output_data['test_cases'].append(test_result)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
        
        print("\n" + "=" * 70)
        print("PHASE 1 COMPLETED SUCCESSFULLY!")
        print("=" * 70)
        print(f"\n[OK] Query results saved to: {output_path}")
        print(f"[OK] Processed {len(eval_data_list)} queries")
        print("\nNext step: Run 'Phase 2: Evaluation' to judge with Gemini")
        
    except Exception as e:
        print(f"\n[ERROR] Phase 1 failed: {e}")
        import traceback
        traceback.print_exc()


def run_evaluation_phase():
    """
    Phase 2: Load saved query results and evaluate with Gemini judge.
    This phase is fast and can be re-run with different configurations.
    """
    print("\n" + "=" * 70)
    print("PHASE 2: GEMINI EVALUATION")
    print("=" * 70)
    print("\nThis will:")
    print("  1. Load query results from query_results.json")
    print("  2. Evaluate with Gemini using 6 RAGAS metrics")
    print("  3. Save evaluation scores")
    print("\nEstimated time: 2-3 minutes")
    print("=" * 70)
    
    try:
        # Load query results
        results_path = "Evaluation/query_results.json"
        print(f"\n[PHASE 2] Loading query results from: {results_path}")
        
        try:
            with open(results_path, 'r', encoding='utf-8') as f:
                saved_data = json.load(f)
        except FileNotFoundError:
            print(f"\n[ERROR] Query results not found at {results_path}")
            print("\nPlease run 'Phase 1: Query Collection' first!")
            return
        
        test_cases = saved_data['test_cases']
        print(f"[PHASE 2] Loaded {len(test_cases)} query results")
        
        # Initialize evaluator for Gemini judge
        print("\n[PHASE 2] Initializing Gemini judge...")
        evaluator = RAGASEvaluator()
        
        # Convert saved data to eval_data format
        eval_data_list = []
        for test_case in test_cases:
            eval_data = {
                'test_id': test_case['test_id'],
                'question': test_case['question'],
                'answer': test_case['answer'],
                'contexts': test_case['contexts'],
                'ground_truth': test_case['ground_truth'],
                'query_type': test_case['query_type'],
                'routed_type': test_case['routed_type'],
                'expected_chunks': test_case['expected_chunks'],
                'retrieved_chunk_ids': test_case['retrieved_chunk_ids']
            }
            eval_data_list.append(eval_data)
        
        # Run RAGAS evaluation
        print("\n[PHASE 2] Running Gemini evaluation...")
        ragas_results = evaluator.evaluate_with_ragas(eval_data_list)
        
        if ragas_results is not None:
            # Print detailed results
            evaluator.print_detailed_results(eval_data_list, ragas_results)
            
            # Save JSON results
            evaluator.save_results(eval_data_list, ragas_results, config.EVALUATION_RESULTS_PATH)
            
            # Generate PDF report
            evaluator.generate_pdf_report(eval_data_list, ragas_results, config.EVALUATION_REPORT_PATH)
            
            print("\n" + "=" * 70)
            print("PHASE 2 COMPLETED SUCCESSFULLY!")
            print("=" * 70)
        else:
            print("\n[ERROR] Evaluation failed. Please check the error messages above.")
    
    except Exception as e:
        print(f"\n[ERROR] Phase 2 failed: {e}")
        import traceback
        traceback.print_exc()


def run_full_evaluation():
    """Main entry point for running RAGAS evaluation."""
    print("\n" + "=" * 70)
    print("RAGAS EVALUATION SYSTEM")
    print("=" * 70)
    print("\nThis will evaluate your RAG system using 6 RAGAS metrics:")
    print("  1. Context Precision - Are retrieved chunks relevant?")
    print("  2. Context Recall - Did we retrieve all necessary chunks?")
    print("  3. Faithfulness - Is the answer grounded in context?")
    print("  4. Answer Relevancy - Does the answer address the question?")
    print("  5. Answer Similarity - Semantic similarity to ground truth?")
    print("  6. Answer Correctness - Factual + semantic correctness?")
    print("\nUsing Gemini as the LLM judge for evaluation.")
    print("=" * 70)
    
    try:
        # Initialize evaluator
        evaluator = RAGASEvaluator()
        
        # Load test dataset
        test_cases = evaluator.load_test_dataset()
        
        # Run all queries and collect data
        eval_data_list = []
        
        for idx, test_case in enumerate(test_cases, 1):
            eval_data = evaluator.run_single_query(test_case, idx, len(test_cases))
            eval_data_list.append(eval_data)
        
        # Save query results to query_results.json
        print(f"\n[SAVING] Saving query results to: {config.QUERY_RESULTS_PATH}")
        with open(config.QUERY_RESULTS_PATH, 'w', encoding='utf-8') as f:
            query_data = {
                "timestamp": datetime.now().isoformat(),
                "total_queries": len(eval_data_list),
                "test_cases": eval_data_list
            }
            json.dump(query_data, f, indent=2, ensure_ascii=False)
        print(f"[OK] Query results saved")
        
        # Run RAGAS evaluation
        ragas_results = evaluator.evaluate_with_ragas(eval_data_list)
        
        if ragas_results is not None:
            # Print detailed results
            evaluator.print_detailed_results(eval_data_list, ragas_results)
            
            # Save results to consistent filename
            evaluator.save_results(eval_data_list, ragas_results, config.EVALUATION_RESULTS_PATH)
            
            # Generate PDF report to consistent filename
            evaluator.generate_pdf_report(eval_data_list, ragas_results, config.EVALUATION_REPORT_PATH)
            
            print("\n" + "=" * 70)
            print("EVALUATION COMPLETED SUCCESSFULLY!")
            print("=" * 70)
        else:
            print("\n[ERROR] Evaluation failed. Please check the error messages above.")
    
    except Exception as e:
        print(f"\n[ERROR] Evaluation failed: {e}")
        import traceback
        traceback.print_exc()


def generate_pdf_from_existing():
    """
    Generate a PDF report from existing evaluation_results.json.
    This is useful when you want to regenerate the PDF without re-running evaluation.
    """
    print("\n" + "=" * 70)
    print("GENERATE PDF REPORT")
    print("=" * 70)
    print("\nThis will:")
    print("  1. Load existing evaluation_results.json")
    print("  2. Generate PDF report")
    print("\nEstimated time: < 10 seconds")
    print("=" * 70)
    
    try:
        # Check if evaluation results exist
        if not os.path.exists(config.EVALUATION_RESULTS_PATH):
            print(f"\n[ERROR] Evaluation results not found at {config.EVALUATION_RESULTS_PATH}")
            print("\nPlease run 'Phase 2: Evaluation Phase' first!")
            return
        
        # Load evaluation results
        print(f"\n[PDF] Loading evaluation results from: {config.EVALUATION_RESULTS_PATH}")
        with open(config.EVALUATION_RESULTS_PATH, 'r', encoding='utf-8') as f:
            eval_results = json.load(f)
        
        print(f"[PDF] Loaded evaluation for {eval_results['total_tests']} tests")
        print(f"[PDF] Evaluation timestamp: {eval_results.get('evaluation_timestamp', 'unknown')}")
        print(f"[PDF] Query results timestamp: {eval_results.get('query_results_timestamp', 'unknown')}")
        
        # Initialize evaluator for PDF generation
        evaluator = RAGASEvaluator()
        
        # Reconstruct eval_data_list from saved results
        eval_data_list = []
        for test in eval_results['test_results']:
            eval_data_list.append({
                'test_id': test['test_id'],
                'question': test['question'],
                'query_type': test['query_type'],
                'routed_type': test['routed_type'],
                'answer': test['answer'],
                'ground_truth': test['ground_truth'],
                'expected_chunks': test['expected_chunks'],
                'retrieved_chunk_ids': test['retrieved_chunk_ids']
            })
        
        # Reconstruct ragas_results (mock pandas DataFrame)
        import pandas as pd
        scores_data = []
        for test in eval_results['test_results']:
            scores_data.append(test['scores'])
        ragas_results = pd.DataFrame(scores_data)
        
        # Create a simple object to mimic ragas results
        class MockRagasResults:
            def __init__(self, df):
                self.df = df
            
            def to_pandas(self):
                return self.df
        
        ragas_results = MockRagasResults(ragas_results)
        
        # Generate PDF
        evaluator.generate_pdf_report(eval_data_list, ragas_results, config.EVALUATION_REPORT_PATH)
        
        print("\n" + "=" * 70)
        print("PDF GENERATION COMPLETED!")
        print("=" * 70)
        
    except Exception as e:
        print(f"\n[ERROR] PDF generation failed: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    run_full_evaluation()

