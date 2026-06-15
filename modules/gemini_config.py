"""
Gemini AI Configuration
Handles model selection and API configuration
"""

import google.generativeai as genai
import streamlit as st

PREFERRED_MODELS = [
    'gemini-3-flash-preview',
    'gemini-2.5-flash',
    'gemini-2.0-flash',
    'gemini-flash-latest',
    'gemini-2.5-pro',
    'gemini-pro-latest',
    'gemini-1.5-flash',
    'gemini-1.5-pro',
    'gemini-pro',
]


def _normalize_model_name(name):
    """Return short model id from full API resource name."""
    return name.split('/')[-1] if '/' in name else name


def _resolve_model_name(api_key):
    """Pick the best available model name for the configured API key."""

    genai.configure(api_key=api_key)

    try:
        available = [
            m.name for m in genai.list_models()
            if 'generateContent' in m.supported_generation_methods
        ]

        if available:
            available_ids = {_normalize_model_name(name): name for name in available}

            for preferred in PREFERRED_MODELS:
                preferred_id = _normalize_model_name(preferred)
                if preferred_id in available_ids:
                    return available_ids[preferred_id]

            return available[0]
    except Exception:
        pass

    last_error = None
    for model_name in PREFERRED_MODELS:
        try:
            model = genai.GenerativeModel(model_name)
            response = model.generate_content("Hello")
            if response.text:
                return model_name
        except Exception as e:
            last_error = e

    raise Exception(
        f"No available Gemini model found. Please check your API key and internet connection. "
        f"Last error: {last_error}"
    )


def get_gemini_model(api_key):
    """
    Get an available Gemini model.

    Args:
        api_key (str): Google Gemini API key

    Returns:
        GenerativeModel: Configured Gemini model
    """

    if 'gemini_model_name' not in st.session_state:
        st.session_state.gemini_model_name = _resolve_model_name(api_key)

    genai.configure(api_key=api_key)
    return genai.GenerativeModel(st.session_state.gemini_model_name)


def list_available_models(api_key):
    """
    List all available Gemini models.

    Args:
        api_key (str): Google Gemini API key

    Returns:
        list: List of available model names
    """

    try:
        genai.configure(api_key=api_key)
        return [
            m.name for m in genai.list_models()
            if 'generateContent' in m.supported_generation_methods
        ]
    except Exception as e:
        st.error(f"Error listing models: {str(e)}")
        return []


def generate_content_with_fallback(api_key, prompt, preferred_models=None):
    """
    Generate content with automatic fallback across preferred Gemini models.
    If a model fails due to rate limits, quota limits, or other runtime errors,
    the function automatically tries the next model in the list.

    Args:
        api_key (str): Google Gemini API key
        prompt (str): Text prompt to generate content for
        preferred_models (list, optional): Custom list of models to try

    Returns:
        google.generativeai.types.GenerateContentResponse: The successful response
    """
    if not preferred_models:
        preferred_models = PREFERRED_MODELS

    genai.configure(api_key=api_key)

    last_error = None
    # If we already have a cached working model, try it first by prioritizing it
    working_model = st.session_state.get('gemini_model_name')
    models_to_try = list(preferred_models)
    if working_model:
        # Normalize and remove duplicates
        working_model_clean = working_model.split('/')[-1]
        models_to_try = [working_model_clean] + [m for m in models_to_try if m.split('/')[-1] != working_model_clean]

    for model_name in models_to_try:
        clean_name = model_name.split('/')[-1]
        try:
            model = genai.GenerativeModel(clean_name)
            response = model.generate_content(prompt)
            if response and response.text:
                st.session_state.gemini_model_name = clean_name
                return response
        except Exception as e:
            last_error = e
            # Silently log to print console for tracking
            print(f"Fallback warning: Model {clean_name} failed with: {str(e)}")
            continue

    # Fallback to any listing models if all preferred fail
    try:
        available = [
            m.name for m in genai.list_models()
            if 'generateContent' in m.supported_generation_methods
        ]
        for name in available:
            clean_name = name.split('/')[-1]
            if clean_name not in models_to_try:
                try:
                    model = genai.GenerativeModel(clean_name)
                    response = model.generate_content(prompt)
                    if response and response.text:
                        st.session_state.gemini_model_name = clean_name
                        return response
                except Exception as e:
                    last_error = e
                    continue
    except Exception:
        pass

    raise Exception(f"All Gemini models failed to generate content. Last error: {last_error}")

