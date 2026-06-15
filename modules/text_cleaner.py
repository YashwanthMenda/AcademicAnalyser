"""
Text Cleaning Module
Preprocesses raw extracted text by removing noise and formatting issues
"""

import re


def clean_text(raw_text):
    """
    Clean and preprocess raw extracted text
    
    Args:
        raw_text (str): Raw text from PDF extraction
        
    Returns:
        str: Cleaned and formatted text
    """
    
    if not raw_text:
        return ""
    
    # Remove extra whitespace and blank lines
    text = re.sub(r'\s+', ' ', raw_text)
    
    # Remove special characters but keep punctuation
    text = re.sub(r'[^\w\s\.\,\;\:\!\?\-\(\)\[\]\{\}\"\'\/\%\&\@\#\$\+\=\*]', '', text)
    
    # Remove repeated punctuation
    text = re.sub(r'([\.!?]){2,}', r'\1', text)
    
    # Remove page numbers (common patterns)
    text = re.sub(r'\b(page|Page|PAGE)\s*\d+\b', '', text)
    text = re.sub(r'\b\d+\s*/\s*\d+\b', '', text)
    
    # Remove URLs
    text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', text)
    
    # Remove email addresses
    text = re.sub(r'\S+@\S+', '', text)
    
    # Remove multiple spaces
    text = re.sub(r' {2,}', ' ', text)
    
    # Remove leading/trailing whitespace
    text = text.strip()
    
    # Split into sentences and rejoin with proper spacing
    sentences = text.split('.')
    sentences = [s.strip() for s in sentences if s.strip()]
    text = '. '.join(sentences)
    
    # Add final period if not present
    if text and not text.endswith('.'):
        text += '.'
    
    return text


def truncate_text(text, max_length=50000):
    """
    Truncate text to maximum length for API limits
    
    Args:
        text (str): Input text
        max_length (int): Maximum character length
        
    Returns:
        str: Truncated text
    """
    
    if len(text) <= max_length:
        return text
    
    # Truncate at sentence boundary
    truncated = text[:max_length]
    last_period = truncated.rfind('.')
    
    if last_period > 0:
        return truncated[:last_period + 1]
    else:
        return truncated


def get_text_stats(text):
    """
    Get statistics about the text
    
    Args:
        text (str): Input text
        
    Returns:
        dict: Statistics dictionary
    """
    
    words = text.split()
    
    return {
        'characters': len(text),
        'words': len(words),
        'sentences': text.count('.') + text.count('!') + text.count('?'),
        'paragraphs': text.count('\n\n') + 1
    }
