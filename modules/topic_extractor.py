"""
Important Topics Extraction Module
Identifies key exam-oriented topics using Gemini AI
"""

import google.generativeai as genai
import streamlit as st
import re


def extract_important_topics(cleaned_text, api_key):
    """
    Extract important topics from content
    
    Args:
        cleaned_text (str): Preprocessed text
        api_key (str): Google Gemini API key
        
    Returns:
        list: List of important topics
    """
    
    try:
        from .gemini_config import generate_content_with_fallback
        
        prompt = get_topics_prompt(cleaned_text)
        
        with st.spinner("🔍 Identifying important topics..."):
            response = generate_content_with_fallback(api_key, prompt)
        
        topics_text = response.text
        topics = parse_topics(topics_text)
        
        if topics:
            st.success(f"✅ Identified {len(topics)} important topics")
            return topics
        else:
            st.warning("⚠️ No topics extracted")
            return []
            
    except Exception as e:
        st.error(f"❌ Topic extraction error: {str(e)}")
        
        if "429" in str(e) or "quota" in str(e).lower():
            st.warning("⚠️ API rate limit reached. Please wait and try again.")
            
        return []


def get_topics_prompt(text):
    """
    Create topic extraction prompt
    
    Args:
        text (str): Content to analyze
        
    Returns:
        str: Formatted prompt
    """
    
    # Truncate if too long
    max_length = 30000
    if len(text) > max_length:
        text = text[:max_length] + "..."
    
    prompt = f"""You are an academic expert analyzing study material.

Your task is to identify the most important topics that a student should focus on for their examination.

**Instructions:**
- Extract 10-15 key topics
- Focus on exam-relevant concepts
- Be specific and clear
- Return as a numbered list (one topic per line)
- Each topic should be concise (2-6 words)
- Prioritize most important topics first

**Study Material:**
{text}

**List the important topics (numbered list, format: 1. Topic Name):**"""
    
    return prompt


def parse_topics(topics_text):
    """
    Parse topics from AI response
    
    Args:
        topics_text (str): Raw response from AI
        
    Returns:
        list: Parsed list of topics
    """
    
    topics = []
    
    # Split by newlines
    lines = topics_text.strip().split('\n')
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        # Remove numbering (e.g., "1.", "1)", "-", "•", "*")
        line = re.sub(r'^\d+[\.\):\-]\s*', '', line)
        line = re.sub(r'^[-•\*]\s*', '', line)
        
        # Remove markdown formatting
        line = line.replace('*', '').replace('_', '').strip()
        
        if line and len(line) > 2:
            topics.append(line)
    
    return topics[:15]  # Limit to 15 topics


def display_topics(topics):
    """
    Display topics in formatted manner
    
    Args:
        topics (list): List of topics
    """
    
    st.markdown("### 📌 IMPORTANT TOPICS")
    st.markdown("---")
    
    if not topics:
        st.info("No topics identified")
        return
    
    # Display in two columns
    col1, col2 = st.columns(2)
    
    mid_point = len(topics) // 2
    
    with col1:
        for idx, topic in enumerate(topics[:mid_point], 1):
            st.markdown(f"**{idx}.** {topic}")
    
    with col2:
        for idx, topic in enumerate(topics[mid_point:], mid_point + 1):
            st.markdown(f"**{idx}.** {topic}")
