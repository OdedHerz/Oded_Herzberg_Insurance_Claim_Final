"""
Reporters for QA Testing Suite

Generates JSON and PDF reports from test results.
"""

from .json_reporter import JSONReporter
from .pdf_reporter import PDFReporter

__all__ = ["JSONReporter", "PDFReporter"]
