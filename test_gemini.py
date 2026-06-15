import os

import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv('GEMINI_API_KEY')

print(f"API Key loaded: {api_key[:10]}..." if api_key else "No API key found")

if not api_key:
    raise SystemExit(1)

genai.configure(api_key=api_key)

print("\nAvailable models:")
available = []
for model in genai.list_models():
    if 'generateContent' in model.supported_generation_methods:
        available.append(model.name)
        print(f"- {model.name}")

if not available:
    print("\nNo models found.")
    raise SystemExit(1)

from modules.gemini_config import generate_content_with_fallback

print("\nTesting generate_content_with_fallback:")
try:
    response = generate_content_with_fallback(api_key, "Hello, this is a test")
    print(f"Success! Response: {response.text[:100]}")
    import streamlit as st
    print(f"Active model in session state: {st.session_state.get('gemini_model_name')}")
except Exception as e:
    print(f"Error testing fallback: {e}")

