"""
Mistake Analysis and Weak Topic Detection Module
Analyzes mistakes and identifies weak areas
"""

import streamlit as st
from collections import Counter


def analyze_mistakes(mistakes):
    """
    Display detailed mistake analysis
    
    Args:
        mistakes (list): List of mistake dictionaries
    """
    
    if not mistakes:
        st.success("🎉 Perfect score! No mistakes to analyze.")
        return
    
    st.markdown("---")
    st.markdown("## ❌ MISTAKE ANALYSIS")
    st.markdown("---")
    
    st.info(f"You made {len(mistakes)} mistake(s). Let's analyze them:")
    
    for mistake in mistakes:
        display_single_mistake(mistake)


def display_single_mistake(mistake):
    """
    Display a single mistake with explanation
    
    Args:
        mistake (dict): Mistake information
    """
    
    with st.expander(f"❌ Question {mistake['question_num']}: {mistake['topic']}", expanded=True):
        
        # Question
        st.markdown("**Question:**")
        st.write(mistake['question'])
        
        st.markdown("---")
        
        # Create two columns for answers
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Your Answer:**")
            if mistake['user_answer'] == "Not answered":
                st.error("❌ " + mistake['user_answer'])
            else:
                st.error("❌ " + mistake['user_answer'])
        
        with col2:
            st.markdown("**Correct Answer:**")
            st.success("✅ " + mistake['correct_answer'])
        
        st.markdown("---")
        
        # Explanation
        st.markdown("**Explanation:**")
        st.info(mistake['explanation'])
        
        # Topic tag
        st.markdown(f"**Topic:** `{mistake['topic']}`")


def detect_weak_topics(mistakes):
    """
    Identify weak topics from mistakes
    
    Args:
        mistakes (list): List of mistakes
        
    Returns:
        list: List of (topic, count) tuples sorted by frequency
    """
    
    if not mistakes:
        return []
    
    # Extract topics from mistakes
    topics = [m['topic'] for m in mistakes]
    
    # Count topic frequencies
    topic_counts = Counter(topics)
    
    # Sort by frequency (most common first)
    weak_topics = topic_counts.most_common()
    
    return weak_topics


def display_weak_topics(weak_topics):
    """
    Display weak topic analysis
    
    Args:
        weak_topics (list): List of (topic, count) tuples
    """
    
    if not weak_topics:
        st.success("🎉 No weak areas detected!")
        return
    
    st.markdown("---")
    st.markdown("## 📉 WEAK AREAS DETECTED")
    st.markdown("---")
    
    st.warning("You need to focus on the following topics:")
    
    for idx, (topic, count) in enumerate(weak_topics, 1):
        mistake_word = "mistake" if count == 1 else "mistakes"
        st.markdown(f"**{idx}.** {topic} — *{count} {mistake_word}*")
        
        # Visual indicator
        st.progress(count / len(weak_topics))


def get_weak_topic_list(weak_topics):
    """
    Get list of weak topic names only
    
    Args:
        weak_topics (list): List of (topic, count) tuples
        
    Returns:
        list: List of topic names
    """
    
    return [topic for topic, count in weak_topics]
