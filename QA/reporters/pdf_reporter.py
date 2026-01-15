"""
PDF Reporter for QA Testing Suite

Generates visual PDF reports from QA test results including:
- Executive summary with overall scores
- Agent performance breakdown
- Detailed test results
- Pass/fail statistics
"""

import sys
import json
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent))

# Import reportlab
try:
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak, Image
    from reportlab.platypus.flowables import HRFlowable
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False


class PDFReporter:
    """
    Generates PDF reports from QA test results.
    
    Creates a comprehensive report with:
    - Executive summary page
    - Agent performance sections
    - Grader comparison
    - Detailed test results
    """
    
    def __init__(self):
        """Initialize the PDF reporter."""
        if not REPORTLAB_AVAILABLE:
            raise ImportError("reportlab package not installed. Run: pip install reportlab")
        
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        """Create custom paragraph styles for the report."""
        # Title style
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1f4788'),
            spaceAfter=30,
            alignment=TA_CENTER
        ))
        
        # Section header style
        self.styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=self.styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#2c5aa0'),
            spaceAfter=12,
            spaceBefore=20
        ))
        
        # Subsection header style
        self.styles.add(ParagraphStyle(
            name='SubsectionHeader',
            parent=self.styles['Heading3'],
            fontSize=12,
            textColor=colors.HexColor('#2c5aa0'),
            spaceAfter=8,
            spaceBefore=12
        ))
        
        # Score style (large, centered)
        self.styles.add(ParagraphStyle(
            name='ScoreStyle',
            parent=self.styles['Normal'],
            fontSize=36,
            textColor=colors.HexColor('#1f4788'),
            alignment=TA_CENTER,
            spaceAfter=10
        ))
    
    def generate_report(self, results: Dict[str, Any], output_path: str):
        """
        Generate a comprehensive PDF report from QA test results.
        
        Args:
            results: Aggregated test results (from JSON reporter)
            output_path: Path to save PDF file
        """
        try:
            # Ensure directory exists
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            
            # Load additional data for detailed reporting
            self._load_supplemental_data(results)
            
            # Create PDF document
            doc = SimpleDocTemplate(
                output_path,
                pagesize=letter,
                rightMargin=72,
                leftMargin=72,
                topMargin=72,
                bottomMargin=18
            )
            
            # Build content
            story = []
            
            # Title page
            story.extend(self._create_title_page(results))
            story.append(PageBreak())
            
            # Executive summary
            story.extend(self._create_executive_summary(results))
            story.append(PageBreak())
            
            # Agent performance
            story.extend(self._create_agent_performance_section(results))
            
            # Detailed results
            if results.get('detailed_results'):
                story.append(PageBreak())
                story.extend(self._create_detailed_results_section(results))
            
            # Build PDF
            doc.build(story)
            
            print(f"[PDF REPORTER] PDF report saved to {output_path}")
            
        except Exception as e:
            print(f"[ERROR] Failed to generate PDF report: {e}")
            import traceback
            traceback.print_exc()
            raise
    
    def _load_supplemental_data(self, results: Dict[str, Any]):
        """
        Load cached answers and test data to enrich the results.
        
        Args:
            results: Results dictionary to enrich with additional data
        """
        try:
            # Get the QA directory path
            qa_dir = Path(__file__).parent.parent
            
            # Load cached answers
            cached_answers_path = qa_dir / "results" / "cached_answers.json"
            if cached_answers_path.exists():
                with open(cached_answers_path, 'r', encoding='utf-8') as f:
                    cached_answers = json.load(f)
                    results['cached_answers'] = cached_answers
            
            # Load test data files
            test_data_dir = qa_dir / "test_data"
            test_data = {}
            
            for test_file in ['needle_tests.json', 'summary_tests.json', 'routing_tests.json', 'hitl_tests.json']:
                test_path = test_data_dir / test_file
                if test_path.exists():
                    with open(test_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        test_type = test_file.replace('_tests.json', '')
                        test_data[test_type] = data.get('tests', [])
            
            results['test_data'] = test_data
            
        except Exception as e:
            print(f"[WARNING] Could not load supplemental data: {e}")
            # Continue without the extra data
    
    def _create_title_page(self, results: Dict[str, Any]) -> list:
        """Create the title page."""
        content = []
        
        # Add spacing from top
        content.append(Spacer(1, 2*inch))
        
        # Title
        title = Paragraph("QA Testing Suite Report", self.styles['CustomTitle'])
        content.append(title)
        content.append(Spacer(1, 0.3*inch))
        
        # Subtitle
        subtitle = Paragraph(
            "Insurance Claim Multi-Agent System",
            self.styles['Heading2']
        )
        content.append(subtitle)
        content.append(Spacer(1, 1*inch))
        
        # Report metadata
        metadata = results.get('metadata', {})
        report_date = metadata.get('report_generated', datetime.now().isoformat())
        
        meta_text = f"""
        <para alignment="center">
        Report Generated: {report_date[:10]}<br/>
        Version: {metadata.get('version', '1.0.0')}
        </para>
        """
        content.append(Paragraph(meta_text, self.styles['Normal']))
        
        return content
    
    def _create_executive_summary(self, results: Dict[str, Any]) -> list:
        """Create the executive summary section."""
        content = []
        
        # Section header
        content.append(Paragraph("Executive Summary", self.styles['SectionHeader']))
        content.append(Spacer(1, 0.2*inch))
        
        content.append(Paragraph(
            '<para alignment="center"><b>Agent Performance Summary</b></para>',
            self.styles['Heading3']
        ))
        content.append(Spacer(1, 0.2*inch))
        
        # Summary table
        overall_scores = results.get('overall_scores', {})
        agent_perf = overall_scores.get('agent_performance', {})
        
        summary_data = [
            ['Agent', 'Score', 'Status']
        ]
        
        for agent_name, score in agent_perf.items():
            status = self._get_status_text(score)
            summary_data.append([
                agent_name.replace('_', ' ').title(),
                f"{score:.1%}",
                status
            ])
        
        summary_table = Table(summary_data, colWidths=[3*inch, 1.5*inch, 1.5*inch])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c5aa0')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey])
        ]))
        
        content.append(summary_table)
        
        return content
    
    def _create_agent_performance_section(self, results: Dict[str, Any]) -> list:
        """Create detailed agent performance section with cross-table format."""
        content = []
        
        content.append(Paragraph("Agent Performance Details", self.styles['SectionHeader']))
        content.append(Spacer(1, 0.2*inch))
        
        agent_scores = results.get('agent_scores', {})
        grader_scores = results.get('grader_scores', {})
        hitl_data = grader_scores.get('hitl_grader', {})
        by_agent_type = hitl_data.get('by_agent_type', {})
        
            # Build cross-table header
        table_data = [
            ['Agent', 'Tests', 'Code\nScore', 'Model\nScore', 'Combined', 'HITL\nTests', 'HITL\nRating', 'HITL\nScore']
        ]
        
        # Define agent order for consistent display
        agent_order = ['needle_agent', 'summary_agent', 'routing_agent']
        
        for agent_name in agent_order:
            if agent_name not in agent_scores:
                continue
                
            agent_data = agent_scores[agent_name]
            if not isinstance(agent_data, dict) or not agent_data:
                continue
            
            # Format agent display name
            display_name = agent_name.replace('_agent', '').title()
            
            # Get basic metrics
            total_tests = agent_data.get('total_tests', 0)
            
            # Code score (use accuracy for routing agent)
            code_score = '-'
            if 'average_code_score' in agent_data and agent_data['average_code_score'] is not None:
                code_score = f"{agent_data['average_code_score']:.1%}"
            elif 'accuracy' in agent_data:  # Routing agent
                code_score = f"{agent_data['accuracy']:.1%}"
            
            # Model score
            model_score = '-'
            if 'average_model_score' in agent_data and agent_data['average_model_score'] is not None:
                model_score = f"{agent_data['average_model_score']:.1%}"
            
            # Combined score
            combined_score = '-'
            if 'average_combined_score' in agent_data and agent_data['average_combined_score'] is not None:
                combined_score = f"{agent_data['average_combined_score']:.1%}"
            elif 'accuracy' in agent_data:  # Routing agent uses accuracy as combined
                combined_score = f"{agent_data['accuracy']:.1%}"
            
            # HITL metrics
            agent_type = agent_name.replace('_agent', '')
            hitl_tests = '-'
            hitl_rating = '-'
            hitl_score = '-'
            
            if agent_type in by_agent_type:
                agent_hitl = by_agent_type[agent_type]
                hitl_tests = str(agent_hitl.get('total_tests', 0))
                hitl_rating = f"{agent_hitl.get('average_rating', 0.0):.2f}/5"
                hitl_score = f"{agent_hitl.get('average_score', 0.0):.1%}"
            
            # Add row to table
            table_data.append([
                display_name,
                str(total_tests),
                code_score,
                model_score,
                combined_score,
                hitl_tests,
                hitl_rating,
                hitl_score
            ])
        
        # Create table with appropriate column widths (wider for better readability)
        col_widths = [1.0*inch, 0.65*inch, 0.9*inch, 0.95*inch, 0.9*inch, 0.85*inch, 0.95*inch, 0.9*inch]
        performance_table = Table(table_data, colWidths=col_widths)
        
        # Apply styling
        performance_table.setStyle(TableStyle([
            # Header styling
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c5aa0')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('TOPPADDING', (0, 0), (-1, 0), 12),
            
            # Data row styling
            ('ALIGN', (0, 1), (0, -1), 'LEFT'),  # Agent names left-aligned
            ('ALIGN', (1, 1), (-1, -1), 'CENTER'),  # All metrics centered
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
            ('TOPPADDING', (0, 1), (-1, -1), 8),
            
            # Grid and alternating rows
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
            
            # Bold agent names
            ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
        ]))
        
        content.append(performance_table)
        content.append(Spacer(1, 0.3*inch))
        
        return content
    
    def _create_grader_comparison_section(self, results: Dict[str, Any]) -> list:
        """Create grader comparison section."""
        content = []
        
        content.append(Paragraph("Grader Performance Comparison", self.styles['SectionHeader']))
        content.append(Spacer(1, 0.2*inch))
        
        grader_scores = results.get('grader_scores', {})
        
        grader_data = [
            ['Grader Type', 'Average Score', 'Tests Graded']
        ]
        
        for grader_name, grader_info in grader_scores.items():
            if isinstance(grader_info, dict) and grader_info:
                avg_score = grader_info.get('average_score', grader_info.get('average_rating', 0.0))
                tests_graded = grader_info.get('total_tests', grader_info.get('completed_tests', '-'))
                
                if avg_score > 0 or tests_graded != '-':
                    grader_data.append([
                        grader_name.replace('_', ' ').title(),
                        f"{avg_score:.1%}",
                        str(tests_graded)
                    ])
        
        if len(grader_data) > 1:
            grader_table = Table(grader_data, colWidths=[2.5*inch, 2*inch, 1.5*inch])
            grader_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c5aa0')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('FONTSIZE', (0, 1), (-1, -1), 10),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey])
            ]))
            content.append(grader_table)
        
        return content
    
    def _create_detailed_results_section(self, results: Dict[str, Any]) -> list:
        """Create detailed test results section."""
        content = []
        
        content.append(Paragraph("Detailed Test Results", self.styles['SectionHeader']))
        content.append(Spacer(1, 0.2*inch))
        
        detailed_results = results.get('detailed_results', {})
        
        # Needle tests
        if detailed_results.get('needle_tests'):
            content.append(Paragraph("Needle Agent Tests", self.styles['SubsectionHeader']))
            content.append(Spacer(1, 0.1*inch))
            content.extend(self._create_test_results_table(detailed_results['needle_tests'], results))
            content.append(Spacer(1, 0.2*inch))
        
        # Summary tests
        if detailed_results.get('summary_tests'):
            content.append(PageBreak())
            content.append(Paragraph("Summary Agent Tests", self.styles['SubsectionHeader']))
            content.append(Spacer(1, 0.1*inch))
            content.extend(self._create_test_results_table(detailed_results['summary_tests'], results))
            content.append(Spacer(1, 0.2*inch))
        
        # Routing tests
        if detailed_results.get('routing_tests'):
            content.append(PageBreak())
            content.append(Paragraph("Routing Agent Tests", self.styles['SubsectionHeader']))
            content.append(Spacer(1, 0.1*inch))
            content.extend(self._create_routing_test_results(detailed_results['routing_tests'], results))
        
        # HITL tests
        if detailed_results.get('hitl_tests'):
            content.append(PageBreak())
            content.append(Paragraph("Human-in-the-Loop (HITL) Tests", self.styles['SubsectionHeader']))
            content.append(Spacer(1, 0.1*inch))
            content.extend(self._create_hitl_test_results(detailed_results['hitl_tests'], results))
        
        return content
    
    def _create_test_results_table(self, test_results: list, results: Dict[str, Any]) -> list:
        """
        Create detailed view showing individual test results.
        
        Args:
            test_results: List of test result dictionaries
            results: Full results including cached answers and test data
            
        Returns:
            List of flowables
        """
        content = []
        
        if not test_results:
            return content
        
        # Summary statistics
        passed_tests = sum(1 for t in test_results if t.get('combined_score', 0) >= 0.7)
        total_tests = len(test_results)
        avg_score = sum(t.get('combined_score', 0) for t in test_results) / total_tests if total_tests > 0 else 0
        
        summary_text = f"""
        <b>Summary:</b> {total_tests} tests | 
        {passed_tests} passed ({100*passed_tests/total_tests:.1f}%) | 
        Average Score: {avg_score:.1%}
        """
        
        content.append(Paragraph(summary_text, self.styles['Normal']))
        content.append(Spacer(1, 0.2*inch))
        
        # Individual test details
        for idx, test_result in enumerate(test_results):
            # Add page break every 2 tests to prevent cramming
            if idx > 0 and idx % 2 == 0:
                content.append(PageBreak())
            
            content.extend(self._create_individual_test_detail(test_result, results))
        
        return content
    
    def _get_score_color(self, score: float) -> str:
        """Get color based on score."""
        if score >= 0.8:
            return '#28a745'  # Green
        elif score >= 0.6:
            return '#ffc107'  # Yellow
        else:
            return '#dc3545'  # Red
    
    def _get_status_text(self, score: float) -> str:
        """Get status text based on score."""
        if score >= 0.8:
            return '✓ Excellent'
        elif score >= 0.6:
            return '~ Good'
        else:
            return '✗ Needs Improvement'
    
    def _get_test_data_by_id(self, test_id: str, results: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Get test data (ground truth, etc.) for a specific test ID.
        
        Args:
            test_id: Test identifier (e.g., 'needle_01')
            results: Results dictionary with test_data
            
        Returns:
            Test data dictionary or None
        """
        test_data = results.get('test_data', {})
        
        # Determine test type from ID
        if test_id.startswith('needle_'):
            test_list = test_data.get('needle', [])
        elif test_id.startswith('summary_'):
            test_list = test_data.get('summary', [])
        elif test_id.startswith('routing_'):
            test_list = test_data.get('routing', [])
        else:
            return None
        
        # Find matching test
        for test in test_list:
            if test.get('id') == test_id:
                return test
        
        return None
    
    def _get_cached_answer(self, test_id: str, results: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Get cached answer for a specific test ID.
        
        Args:
            test_id: Test identifier
            results: Results dictionary with cached_answers
            
        Returns:
            Cached answer dictionary or None
        """
        cached_answers = results.get('cached_answers', {})
        
        # Check in different answer categories
        for key in ['needle_answers', 'summary_answers', 'routing_answers']:
            answers = cached_answers.get(key, {})
            if test_id in answers:
                return answers[test_id]
        
        return None
    
    def _create_individual_test_detail(self, test_result: Dict[str, Any], results: Dict[str, Any]) -> list:
        """
        Create detailed view for a single test.
        
        Args:
            test_result: Test result data
            results: Full results including cached answers and test data
            
        Returns:
            List of flowables for the test detail
        """
        content = []
        
        test_id = test_result.get('test_id', 'Unknown')
        combined_score = test_result.get('combined_score', 0.0)
        
        # Get additional data
        test_data = self._get_test_data_by_id(test_id, results)
        cached_answer = self._get_cached_answer(test_id, results)
        
        # Test header with ID and score
        score_color = self._get_score_color(combined_score)
        status_symbol = '✓' if combined_score >= 0.7 else '✗'
        
        header_text = f'<font color="{score_color}"><b>Test {test_id}</b></font>'
        header_text += f'<font color="{score_color}" size="14"> (Score: {combined_score:.1%} {status_symbol})</font>'
        content.append(Paragraph(header_text, self.styles['SubsectionHeader']))
        content.append(HRFlowable(width="100%", thickness=1, color=colors.grey, spaceAfter=10))
        
        # Question
        if test_data:
            question = test_data.get('question', 'N/A')
            content.append(Paragraph(f'<b>Question:</b> {question}', self.styles['Normal']))
            content.append(Spacer(1, 0.1*inch))
        
        # Agent's Answer
        if cached_answer:
            answer = cached_answer.get('answer', 'N/A')
            # Escape XML special characters and limit length
            answer = answer.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
            if len(answer) > 2000:
                answer = answer[:2000] + '...'
            content.append(Paragraph(f'<b>Agent Answer:</b>', self.styles['Normal']))
            content.append(Paragraph(answer, self.styles['Normal']))
            content.append(Spacer(1, 0.1*inch))
        
        # Ground Truth
        if test_data:
            ground_truth = test_data.get('ground_truth', 'N/A')
            ground_truth = ground_truth.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
            content.append(Paragraph(f'<b>Ground Truth:</b>', self.styles['Normal']))
            content.append(Paragraph(ground_truth, self.styles['Normal']))
            content.append(Spacer(1, 0.1*inch))
        
        # Code Grader Results (only show if there are actual results)
        code_grader = test_result.get('code_grader', {})
        if code_grader and code_grader.get('score') is not None:
            content.extend(self._create_code_grader_details(code_grader))
            content.append(Spacer(1, 0.1*inch))
        
        # Model Grader Results
        if 'model_grader' in test_result and test_result['model_grader']:
            content.extend(self._create_model_grader_details(test_result['model_grader']))
            content.append(Spacer(1, 0.1*inch))
        
        # Sources
        if cached_answer and cached_answer.get('sources'):
            content.extend(self._format_sources_list(cached_answer['sources']))
        
        # Separator line
        content.append(Spacer(1, 0.15*inch))
        content.append(HRFlowable(width="100%", thickness=1, color=colors.lightgrey, spaceAfter=15))
        
        return content
    
    def _create_code_grader_details(self, code_grader: Dict[str, Any]) -> list:
        """
        Format code grader check results.
        
        Args:
            code_grader: Code grader results
            
        Returns:
            List of flowables
        """
        content = []
        
        score = code_grader.get('score', 0.0)
        score_color = self._get_score_color(score)
        
        content.append(Paragraph(
            f'<font size="10"><b>CODE GRADER</b></font> <font color="{score_color}">({score:.1%})</font>',
            self.styles['Normal']
        ))
        
        checks = code_grader.get('checks', {})
        if checks:
            check_data = []
            for check_name, check_result in checks.items():
                if isinstance(check_result, dict):
                    passed = check_result.get('passed', False)
                    matched = check_result.get('matched', 'N/A')
                    symbol = '✓' if passed else '✗'
                    color = '#28a745' if passed else '#dc3545'
                    
                    # Escape and truncate matched value
                    matched_str = str(matched).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
                    if len(matched_str) > 60:
                        matched_str = matched_str[:60] + '...'
                    
                    check_data.append([
                        Paragraph(f'<font color="{color}">{symbol}</font>', self.styles['Normal']),
                        Paragraph(check_name.replace('_', ' ').title(), self.styles['Normal']),
                        Paragraph(matched_str, self.styles['Normal'])
                    ])
            
            if check_data:
                check_table = Table(check_data, colWidths=[0.3*inch, 2*inch, 3*inch])
                check_table.setStyle(TableStyle([
                    ('ALIGN', (0, 0), (0, -1), 'CENTER'),
                    ('ALIGN', (1, 0), (-1, -1), 'LEFT'),
                    ('FONTSIZE', (0, 0), (-1, -1), 9),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
                    ('TOPPADDING', (0, 0), (-1, -1), 3),
                ]))
                content.append(check_table)
        
        return content
    
    def _create_model_grader_details(self, model_grader: Dict[str, Any]) -> list:
        """
        Format model grader criterion scores.
        
        Args:
            model_grader: Model grader results
            
        Returns:
            List of flowables
        """
        content = []
        
        overall_score = model_grader.get('overall_score', model_grader.get('scores', {}).get('overall_score', 0.0))
        score_color = self._get_score_color(overall_score)
        
        content.append(Paragraph(
            f'<font size="10"><b>MODEL GRADER</b></font> <font color="{score_color}">({overall_score:.1%})</font>',
            self.styles['Normal']
        ))
        
        scores = model_grader.get('scores', {})
        if scores:
            score_data = []
            for criterion, score_val in scores.items():
                if criterion not in ['overall_score', 'reasoning'] and isinstance(score_val, (int, float)):
                    score_data.append([
                        Paragraph(criterion.replace('_', ' ').title(), self.styles['Normal']),
                        Paragraph(f'{score_val:.1%}', self.styles['Normal'])
                    ])
            
            if score_data:
                score_table = Table(score_data, colWidths=[2.5*inch, 1*inch])
                score_table.setStyle(TableStyle([
                    ('ALIGN', (0, 0), (0, -1), 'LEFT'),
                    ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
                    ('FONTSIZE', (0, 0), (-1, -1), 9),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
                    ('TOPPADDING', (0, 0), (-1, -1), 3),
                ]))
                content.append(score_table)
        
        # Reasoning
        reasoning = model_grader.get('reasoning', scores.get('reasoning', ''))
        if reasoning:
            reasoning_text = str(reasoning).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
            if len(reasoning_text) > 400:
                reasoning_text = reasoning_text[:400] + '...'
            content.append(Paragraph(f'<i>Reasoning: {reasoning_text}</i>', self.styles['Normal']))
        
        return content
    
    def _format_sources_list(self, sources: List[Dict[str, Any]]) -> list:
        """
        Display source references.
        
        Args:
            sources: List of source dictionaries
            
        Returns:
            List of flowables
        """
        content = []
        
        if not sources:
            return content
        
        content.append(Paragraph('<b>Sources:</b>', self.styles['Normal']))
        
        source_items = []
        for idx, source in enumerate(sources[:3]):  # Limit to 3 sources
            page = source.get('page', 'N/A')
            header = source.get('header', 'N/A')
            header = str(header).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
            if len(header) > 50:
                header = header[:50] + '...'
            source_items.append(f'Page {page}: {header}')
        
        source_text = ' | '.join(source_items)
        content.append(Paragraph(source_text, self.styles['Normal']))
        
        return content
    
    def _create_hitl_test_results(self, hitl_tests: list, results: Dict[str, Any]) -> list:
        """
        Create detailed display for HITL test results.
        
        Args:
            hitl_tests: List of HITL test results
            results: Full results dictionary
            
        Returns:
            List of flowables
        """
        content = []
        
        if not hitl_tests:
            return content
        
        # Summary statistics
        total_tests = len(hitl_tests)
        avg_rating = sum(t.get('rating', 0) for t in hitl_tests) / total_tests if total_tests > 0 else 0
        avg_score = sum(t.get('score', 0) for t in hitl_tests) / total_tests if total_tests > 0 else 0
        
        summary_text = f"""
        <b>Summary:</b> {total_tests} tests reviewed | 
        Average Rating: {avg_rating:.2f}/5 | 
        Average Score: {avg_score:.1%}
        """
        
        content.append(Paragraph(summary_text, self.styles['Normal']))
        content.append(Spacer(1, 0.2*inch))
        
        # Individual HITL test details
        for idx, test in enumerate(hitl_tests):
            # Add page break every 3 tests (HITL entries are longer)
            if idx > 0 and idx % 3 == 0:
                content.append(PageBreak())
            
            test_id = test.get('test_id', 'Unknown')
            rating = test.get('rating', 0)
            score = test.get('score', 0)
            feedback = test.get('feedback', '')
            query_type = test.get('query_type', 'unknown')
            evaluation_type = test.get('evaluation_type', 'rating')
            
            # Status color based on rating
            if rating >= 4:
                status_color = '#28a745'  # Green
            elif rating >= 3:
                status_color = '#ffc107'  # Yellow
            else:
                status_color = '#dc3545'  # Red
            
            # Get question and answer from test data
            test_data_cache = results.get('test_data', {})
            cached_answers = results.get('cached_answers', {})
            
            question = 'N/A'
            answer = 'N/A'
            expected_route = None
            
            # HITL test IDs may have hitl_ prefix, need to look up in hitl_tests.json
            test_list = test_data_cache.get('hitl', [])
            for t in test_list:
                if t.get('id') == test_id:
                    question = t.get('question', 'N/A')
                    query_type = t.get('query_type', query_type)
                    expected_route = t.get('expected_route')
                    break
            
            # For routing tests, display differently
            if query_type == 'routing' and evaluation_type == 'binary':
                # Test header with binary result
                result_text = 'CORRECT' if score == 1.0 else 'INCORRECT'
                header_text = f'<font color="{status_color}"><b>Test {test_id}</b> (Routing: {result_text})</font>'
                content.append(Paragraph(header_text, self.styles['SubsectionHeader']))
                content.append(HRFlowable(width="100%", thickness=1, color=colors.grey, spaceAfter=10))
                
                # Get actual route
                actual_route = test.get('actual_route', 'N/A')
                
                content.append(Paragraph(f'<b>Question:</b> {question}', self.styles['Normal']))
                content.append(Spacer(1, 0.1*inch))
                
                # Routing decision info
                routing_data = [
                    ['Routing Decision:', actual_route.upper() if actual_route else 'N/A'],
                    ['Human Feedback:', f'{result_text} {"✓" if score == 1.0 else "✗"}'],
                    ['Score:', f'{score:.1%}']
                ]
                
                if feedback:
                    routing_data.append(['Feedback:', feedback[:200] + ('...' if len(feedback) > 200 else '')])
                
                routing_table = Table(routing_data, colWidths=[1.5*inch, 4*inch])
                routing_table.setStyle(TableStyle([
                    ('ALIGN', (0, 0), (0, -1), 'LEFT'),
                    ('ALIGN', (1, 0), (1, -1), 'LEFT'),
                    ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, -1), 10),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                    ('TOPPADDING', (0, 0), (-1, -1), 6),
                    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                    ('TEXTCOLOR', (1, 2), (1, 2), colors.HexColor(status_color))
                ]))
                content.append(routing_table)
                content.append(Spacer(1, 0.2*inch))
                
            else:
                # Standard rating evaluation (for needle/summary tests)
                # Test header
                header_text = f'<font color="{status_color}"><b>Test {test_id}</b> (Rating: {rating}/5)</font>'
                content.append(Paragraph(header_text, self.styles['SubsectionHeader']))
                content.append(HRFlowable(width="100%", thickness=1, color=colors.grey, spaceAfter=10))
                
                # Find answer from cached data
                cache_key = f"{query_type}_answers"
                if cache_key in cached_answers and test_id in cached_answers[cache_key]:
                    answer = cached_answers[cache_key][test_id].get('answer', 'N/A')
                
                content.append(Paragraph(f'<b>Question:</b> {question}', self.styles['Normal']))
                content.append(Spacer(1, 0.1*inch))
                
                content.append(Paragraph(f'<b>Agent Answer:</b> {answer[:2000]}{"..." if len(answer) > 2000 else ""}', 
                                       self.styles['Normal']))
                content.append(Spacer(1, 0.1*inch))
                
                # Rating info
                rating_data = [
                    ['Rating:', f'{rating}/5'],
                    ['Score:', f'{score:.1%}'],
                    ['Query Type:', query_type.title()]
                ]
                
                if feedback:
                    rating_data.append(['Feedback:', feedback[:200] + ('...' if len(feedback) > 200 else '')])
                
                rating_table = Table(rating_data, colWidths=[1.5*inch, 4*inch])
                rating_table.setStyle(TableStyle([
                    ('ALIGN', (0, 0), (0, -1), 'LEFT'),
                    ('ALIGN', (1, 0), (1, -1), 'LEFT'),
                    ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, -1), 10),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                    ('TOPPADDING', (0, 0), (-1, -1), 6),
                    ('VALIGN', (0, 0), (-1, -1), 'TOP')
                ]))
                content.append(rating_table)
                content.append(Spacer(1, 0.2*inch))
        
        return content
    
    def _create_routing_test_results(self, routing_tests: list, results: Dict[str, Any]) -> list:
        """
        Create detailed display for routing test results.
        
        Args:
            routing_tests: List of routing test results
            results: Full results dictionary
            
        Returns:
            List of flowables
        """
        content = []
        
        if not routing_tests:
            return content
        
        # Summary statistics
        passed_tests = sum(1 for t in routing_tests if t.get('passed', False))
        total_tests = len(routing_tests)
        accuracy = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        summary_text = f"""
        <b>Summary:</b> {total_tests} tests | 
        {passed_tests} correct ({accuracy:.1f}%) | 
        Routing Accuracy: {accuracy:.1f}%
        """
        
        content.append(Paragraph(summary_text, self.styles['Normal']))
        content.append(Spacer(1, 0.2*inch))
        
        # Individual routing test details
        for idx, test in enumerate(routing_tests):
            # Add page break every 5 tests
            if idx > 0 and idx % 5 == 0:
                content.append(PageBreak())
            
            test_id = test.get('test_id', 'Unknown')
            passed = test.get('passed', False)
            actual_route = test.get('actual_route', 'N/A')
            expected_route = test.get('expected_route', 'N/A')
            
            # Status symbol and color
            status_symbol = '✓' if passed else '✗'
            status_color = '#28a745' if passed else '#dc3545'
            
            # Test header
            header_text = f'<font color="{status_color}"><b>Test {test_id}</b> ({status_symbol})</font>'
            content.append(Paragraph(header_text, self.styles['SubsectionHeader']))
            content.append(HRFlowable(width="100%", thickness=1, color=colors.grey, spaceAfter=10))
            
            # Get question from test data
            test_data_cache = results.get('test_data', {})
            test_list = test_data_cache.get('routing', [])
            question = 'N/A'
            for t in test_list:
                if t.get('id') == test_id:
                    question = t.get('question', 'N/A')
                    break
            
            content.append(Paragraph(f'<b>Question:</b> {question}', self.styles['Normal']))
            content.append(Spacer(1, 0.1*inch))
            
            # Routing decision
            route_data = [
                ['Expected Route:', expected_route.title()],
                ['Actual Route:', actual_route.title()],
                ['Result:', 'CORRECT ✓' if passed else 'INCORRECT ✗']
            ]
            
            route_table = Table(route_data, colWidths=[2*inch, 3*inch])
            route_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (0, -1), 'LEFT'),
                ('ALIGN', (1, 0), (1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ('TOPPADDING', (0, 0), (-1, -1), 6),
                ('TEXTCOLOR', (1, 2), (1, 2), colors.HexColor(status_color))
            ]))
            content.append(route_table)
            
            # Separator
            content.append(Spacer(1, 0.15*inch))
            content.append(HRFlowable(width="100%", thickness=1, color=colors.lightgrey, spaceAfter=15))
        
        return content


# Example usage
if __name__ == "__main__":
    try:
        reporter = PDFReporter()
        
        # Example results
        example_results = {
            'metadata': {
                'report_generated': datetime.now().isoformat(),
                'version': '1.0.0'
            },
            'overall_scores': {
                'system_score': 0.85,
                'agent_performance': {
                    'needle_agent': 0.88,
                    'summary_agent': 0.82,
                    'routing_agent': 0.95
                }
            },
            'agent_scores': {
                'needle_agent': {
                    'total_tests': 20,
                    'average_code_score': 0.90,
                    'average_model_score': 0.86,
                    'average_combined_score': 0.88
                },
                'summary_agent': {
                    'total_tests': 15,
                    'average_code_score': 0.80,
                    'average_model_score': 0.84,
                    'average_combined_score': 0.82
                },
                'routing_agent': {
                    'total_tests': 10,
                    'accuracy': 0.95
                }
            },
            'grader_scores': {
                'code_grader': {'average_score': 0.85},
                'model_grader': {'average_score': 0.85},
                'hitl_grader': {'average_score': 0.90, 'completed_tests': 10}
            },
            'detailed_results': {
                'needle_tests': [
                    {'test_id': 'needle_01', 'combined_score': 0.9}
                ],
                'summary_tests': [],
                'routing_tests': []
            }
        }
        
        reporter.generate_report(example_results, "test_report.pdf")
        print("Test PDF generated successfully!")
        
    except Exception as e:
        print(f"Error: {e}")
