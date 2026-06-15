"""
AcademicAnalyser Modules Package
"""

from .pdf_reader import extract_text_from_pdf
from .text_cleaner import clean_text
from .summary import generate_summary
from .topic_extractor import extract_important_topics
from .quiz_generator import generate_quiz, display_question
from .evaluator import evaluate_quiz, display_score_report
from .mistake_analysis import analyze_mistakes, detect_weak_topics, display_weak_topics
from .recommendation import generate_revision_plan, display_revision_plan

__all__ = [
    'extract_text_from_pdf',
    'clean_text',
    'generate_summary',
    'extract_important_topics',
    'generate_quiz',
    'display_question',
    'evaluate_quiz',
    'display_score_report',
    'analyze_mistakes',
    'detect_weak_topics',
    'display_weak_topics',
    'generate_revision_plan',
    'display_revision_plan'
]
