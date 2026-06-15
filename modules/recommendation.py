"""
Revision Recommendation Module
Generates personalized revision plans using Gemini AI
"""

import google.generativeai as genai
import streamlit as st


def generate_revision_plan(weak_topics, api_key):
    """
    Generate personalized revision recommendations
    
    Args:
        weak_topics (list): List of weak topic names
        api_key (str): Google Gemini API key
        
    Returns:
        str: Revision plan text
    """
    
    if not weak_topics:
        return "Great job! No specific areas need revision. Continue your excellent work!"
    
    try:
        from .gemini_config import generate_content_with_fallback
        
        prompt = get_revision_prompt(weak_topics)
        
        with st.spinner("📚 Creating personalized revision plan..."):
            response = generate_content_with_fallback(api_key, prompt)
        
        revision_plan = response.text
        
        if revision_plan:
            st.success("✅ Revision plan created")
            return revision_plan
        else:
            return "Unable to generate revision plan. Please review the weak topics manually."
            
    except Exception as e:
        st.error(f"❌ Revision plan generation error: {str(e)}")
        return "Unable to generate revision plan. Please review the weak topics manually."


def get_revision_prompt(weak_topics):
    """
    Create revision recommendation prompt
    
    Args:
        weak_topics (list): List of weak topics
        
    Returns:
        str: Formatted prompt
    """
    
    topics_str = "\n".join([f"- {topic}" for topic in weak_topics])
    
    prompt = f"""You are an experienced academic advisor helping a student improve their understanding.

A student has completed a quiz and performed poorly in the following topics:

{topics_str}

**Your task:**
Create a detailed, structured revision plan that helps the student strengthen their understanding of these topics.

**Include:**
1. Specific subtopics and concepts to review
2. Key points to focus on
3. Practical study tips
4. Suggested study order (if applicable)
5. Important formulas, definitions, or principles
6. Common mistakes to avoid

**Format:**
Use clear headings, bullet points, and structured sections for easy reading.

**Generate the revision plan:**"""
    
    return prompt


def display_revision_plan(revision_plan):
    """
    Display revision plan in formatted manner
    
    Args:
        revision_plan (str): Generated revision plan
    """
    
    st.markdown("---")
    st.markdown("## 📚 PERSONALIZED REVISION PLAN")
    st.markdown("---")
    
    st.info("Based on your quiz performance, here's your customized study plan:")
    
    st.markdown(revision_plan)
    
    st.markdown("---")
    st.success("💡 **Tip:** Focus on understanding concepts rather than memorizing. Practice with more examples!")
