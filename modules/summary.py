"""
Summary Generation Module
Uses Google Gemini AI to generate concise academic summaries
"""

import google.generativeai as genai
import streamlit as st
import time


def generate_summary(cleaned_text, api_key):
    """
    Generate academic summary using Gemini AI
    
    Args:
        cleaned_text (str): Preprocessed text from PDF
        api_key (str): Google Gemini API key
        
    Returns:
        str: Generated summary
    """
    
    try:
        from .gemini_config import generate_content_with_fallback
        
        # Create prompt
        prompt = get_summary_prompt(cleaned_text)
        
        # Show processing message
        with st.spinner("🤖 Generating summary using AI..."):
            response = generate_content_with_fallback(api_key, prompt)
            summary = response.text
        
        if summary:
            st.success("✅ Summary generated successfully")
            return summary
        else:
            st.error("❌ Failed to generate summary")
            return None
            
    except Exception as e:
        st.error(f"❌ Summary generation error: {str(e)}")
        
        if "429" in str(e) or "quota" in str(e).lower():
            st.warning("⚠️ API rate limit reached. Please wait 60 seconds and try again.")
            
        return None


def get_summary_prompt(text):
    """
    Create summary generation prompt
    
    Args:
        text (str): Content to summarize
        
    Returns:
        str: Formatted prompt
    """
    
    # Truncate if too long
    max_length = 30000
    if len(text) > max_length:
        text = text[:max_length] + "..."
    
    prompt = f"""You are an expert academic assistant helping students study efficiently.

Your task is to create a comprehensive yet concise summary of the following study material.

**Instructions:**
- Create clear, well-organized bullet points
- Focus on key definitions, concepts, and important facts
- Use simple language that students can easily understand
- Highlight exam-relevant information
- Structure the summary logically with sections/headings
- Include important formulas, theories, or principles if present
- Keep it concise but complete

**Study Material:**
{text}

**Generate a structured summary:**"""
    
    return prompt
