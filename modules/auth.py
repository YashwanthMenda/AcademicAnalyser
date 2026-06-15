"""
Authentication UI and Google OAuth handling.
"""

import os
import random
import time
import smtplib
from email.mime.text import MIMEText

import requests
import streamlit as st
from google_auth_oauthlib.flow import Flow

from .auth_db import (
    authenticate_user,
    create_user,
    get_or_create_google_user,
    init_db,
    user_exists,
    reset_user_password,
)

AUTH_CSS = """
<style>
    /* Reset and Layout */
    [data-testid="stAppViewContainer"] {
        background-color: #f4f3fa !important; /* light lavender background */
    }
    [data-testid="stHeader"], [data-testid="stToolbar"] {
        background: rgba(0, 0, 0, 0) !important;
        display: none !important;
    }
    section[data-testid="stSidebar"] {
        display: none !important;
    }
    [data-testid="collapsedControl"] {
        display: none !important;
    }
    
    /* Remove padding of main block container on login */
    .main .block-container {
        padding: 0 !important;
        max-width: 100% !important;
    }
    
    /* Outer logo branding on top left of page */
    .auth-outer-header {
        position: fixed;
        top: 2rem;
        left: 3.5rem;
        display: flex;
        align-items: center;
        gap: 0.75rem;
        z-index: 0;
        font-family: system-ui, -apple-system, sans-serif;
    }
    .auth-outer-logo {
        display: flex;
        align-items: center;
        justify-content: center;
    }
    .auth-outer-text {
        display: flex;
        flex-direction: column;
    }
    .auth-outer-title {
        font-size: 1.6rem;
        font-weight: 800;
        color: #1e1b4b; /* deep indigo */
        line-height: 1.2;
    }
    .auth-outer-subtitle {
        font-size: 0.95rem;
        color: #6b7280;
        font-weight: 500;
        margin-top: 0.1rem;
    }
    
    /* Main Dashboard application container box */
    .auth-main-wrapper {
        position: fixed;
        top: 6.5rem;
        left: 3.5rem;
        right: 3.5rem;
        bottom: 3.5rem;
        background-color: #ffffff;
        border-radius: 24px;
        border: 1px solid #e5e7eb;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.04);
        display: flex;
        overflow: hidden;
        z-index: 0;
        font-family: system-ui, -apple-system, sans-serif;
    }
    
    /* Sidebar */
    .auth-sidebar {
        width: 240px;
        height: 100%;
        background-color: #ffffff;
        border-right: 1px solid #f3f4f6;
        display: flex;
        flex-direction: column;
        padding: 2rem 1.25rem;
        box-sizing: border-box;
    }
    .auth-sidebar-logo {
        display: flex;
        align-items: center;
        margin-bottom: 2rem;
        padding-left: 0.5rem;
    }
    .auth-sidebar-menu {
        display: flex;
        flex-direction: column;
        gap: 0.75rem;
    }
    .auth-menu-item {
        display: flex;
        align-items: center;
        gap: 0.75rem;
        font-size: 0.95rem;
        font-weight: 600;
        color: #4b5563;
        padding: 0.75rem 1rem;
        border-radius: 10px;
        cursor: pointer;
        transition: all 0.2s;
    }
    .auth-menu-item.active {
        background-color: #eef2ff;
        color: #6366f1;
    }
    .auth-menu-icon {
        font-size: 1.2rem;
    }
    
    /* Main pane */
    .auth-main-pane {
        flex: 1;
        display: flex;
        flex-direction: column;
        height: 100%;
        background-color: #ffffff;
        box-sizing: border-box;
    }
    
    /* Navbar */
    .auth-navbar {
        height: 70px;
        border-bottom: 1px solid #f3f4f6;
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 0 2rem;
        box-sizing: border-box;
    }
    .auth-nav-tabs {
        display: flex;
        gap: 2rem;
    }
    .auth-nav-tab {
        font-size: 0.95rem;
        font-weight: 600;
        color: #6b7280;
        cursor: pointer;
        padding-bottom: 1.5rem;
        border-bottom: 2px solid transparent;
        transition: all 0.2s;
        margin-top: 0.5rem;
    }
    .auth-nav-tab.active {
        color: #6366f1;
        border-bottom-color: #6366f1;
    }
    .auth-avatar {
        width: 38px;
        height: 38px;
        border-radius: 50%;
        background-color: #c7d2fe;
        color: #4f46e5;
        font-weight: 700;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 0.95rem;
    }
    
    /* Scroll content area */
    .auth-dashboard-content {
        flex: 1;
        padding: 2rem;
        box-sizing: border-box;
        overflow-y: auto;
        display: flex;
        flex-direction: column;
        gap: 2rem;
        background-color: #fafbfc;
    }
    .auth-grid-row {
        display: grid;
        grid-template-columns: 1.15fr 1.25fr;
        gap: 2rem;
    }
    .auth-col-left, .auth-col-right {
        display: flex;
        flex-direction: column;
        gap: 1.5rem;
    }
    
    /* Cards */
    .auth-card-welcome {
        background-color: #ffffff;
        border: 1px solid #e5e7eb;
        border-radius: 16px;
        padding: 1.5rem;
    }
    .auth-card-welcome h3 {
        margin-top: 0;
        margin-bottom: 0.5rem;
        font-size: 1.2rem;
        font-weight: 700;
        color: #1f2937;
    }
    .auth-card-welcome p {
        margin: 0;
        font-size: 0.9rem;
        color: #6b7280;
        line-height: 1.5;
    }
    
    .auth-card-recent {
        background-color: #ffffff;
        border: 1px solid #e5e7eb;
        border-radius: 16px;
        padding: 1.5rem;
        display: flex;
        flex-direction: column;
        gap: 1rem;
    }
    .auth-card-header {
        font-size: 1.05rem;
        font-weight: 700;
        color: #1f2937;
        margin-bottom: 0.25rem;
    }
    .auth-pdf-list {
        display: flex;
        flex-direction: column;
        gap: 0.75rem;
    }
    .auth-pdf-item {
        display: flex;
        align-items: center;
        gap: 0.75rem;
        padding: 0.5rem 0;
    }
    .auth-pdf-icon {
        font-size: 1.5rem;
    }
    .auth-pdf-name {
        font-size: 0.9rem;
        font-weight: 600;
        color: #374151;
    }
    .auth-pdf-meta {
        font-size: 0.75rem;
        color: #9ca3af;
        margin-top: 0.1rem;
    }
    .auth-view-all-link {
        font-size: 0.85rem;
        font-weight: 600;
        color: #6366f1;
        cursor: pointer;
        margin-top: 0.5rem;
    }
    
    /* Stats Grid */
    .auth-stats-grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 1rem;
    }
    .auth-stat-card {
        background-color: #ffffff;
        border: 1px solid #e5e7eb;
        border-radius: 12px;
        padding: 1rem;
        display: flex;
        align-items: center;
        gap: 0.75rem;
    }
    .auth-stat-icon {
        width: 40px;
        height: 40px;
        border-radius: 10px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.3rem;
    }
    .auth-stat-num {
        font-size: 1.25rem;
        font-weight: 700;
        color: #1f2937;
    }
    .auth-stat-label {
        font-size: 0.75rem;
        color: #6b7280;
        font-weight: 500;
        margin-top: 0.1rem;
    }
    
    /* Progress Card */
    .auth-card-progress {
        background-color: #ffffff;
        border: 1px solid #e5e7eb;
        border-radius: 16px;
        padding: 1.5rem;
        display: flex;
        flex-direction: column;
        gap: 1rem;
    }
    .auth-chart-container {
        display: flex;
        flex-direction: column;
        gap: 0.5rem;
    }
    .auth-chart-labels {
        display: flex;
        justify-content: space-between;
        padding: 0 0.5rem;
        font-size: 0.75rem;
        color: #9ca3af;
        font-weight: 500;
    }
    
    /* AI Features section */
    .auth-features-section {
        display: flex;
        flex-direction: column;
        gap: 1rem;
    }
    .auth-section-title {
        font-size: 1.1rem;
        font-weight: 700;
        color: #1f2937;
    }
    .auth-features-grid {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 1rem;
    }
    .auth-feature-card {
        background-color: #ffffff;
        border: 1px solid #e5e7eb;
        border-radius: 12px;
        padding: 1.25rem;
        display: flex;
        flex-direction: column;
        gap: 0.5rem;
    }
    .auth-feature-icon {
        width: 36px;
        height: 36px;
        border-radius: 8px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.2rem;
        margin-bottom: 0.25rem;
    }
    .auth-feature-name {
        font-size: 0.9rem;
        font-weight: 700;
        color: #1f2937;
    }
    .auth-feature-desc {
        font-size: 0.75rem;
        color: #6b7280;
        line-height: 1.4;
    }
    
    /* Blur overlay over the dashboard background */
    .auth-overlay-blur {
        position: fixed;
        inset: 0;
        background: rgba(244, 243, 250, 0.4);
        backdrop-filter: blur(8px) !important;
        -webkit-backdrop-filter: blur(8px) !important;
        z-index: 1;
        pointer-events: none;
    }
    
    /* Login Modal Style: Centered Column Box */
    div[data-testid="stHorizontalBlock"] div[data-testid="column"]:nth-of-type(2) {
        position: fixed !important;
        top: 50% !important;
        left: 50% !important;
        transform: translate(-50%, -50%) !important;
        width: 420px !important;
        max-height: calc(100vh - 80px) !important; /* leave at least 40px space above and below */
        overflow-y: auto !important;
        scrollbar-width: none !important; /* Hide Firefox scrollbar */
        -ms-overflow-style: none !important; /* Hide IE scrollbar */
        background-color: #1e1c26 !important; /* Lite black background */
        border-radius: 16px !important;
        padding: 36px !important;
        box-shadow: 0 15px 40px rgba(0, 0, 0, 0.35) !important;
        z-index: 1000 !important;
        border: 1px solid #2d2a3a !important;
    }
    /* Reset styles for nested columns so they don't look like cards */
    div[data-testid="column"] div[data-testid="stHorizontalBlock"] div[data-testid="column"]:nth-of-type(2) {
        position: static !important;
        transform: none !important;
        width: auto !important;
        max-height: none !important;
        background-color: transparent !important;
        border-radius: 0 !important;
        padding: 0 !important;
        box-shadow: none !important;
        z-index: auto !important;
        border: none !important;
    }
    div[data-testid="stHorizontalBlock"] div[data-testid="column"]:nth-of-type(2)::-webkit-scrollbar {
        display: none !important; /* Hide Chrome/Safari scrollbar */
    }
    
    /* Title and description inside modal */
    .auth-title {
        text-align: center;
        font-size: 24px;
        font-weight: 800;
        color: #ffffff !important; /* white title */
        margin-bottom: 0.5rem;
        font-family: system-ui, -apple-system, sans-serif;
    }
    .auth-title span {
        color: #6366f1 !important; /* purple/violet */
    }
    .auth-subtitle {
        text-align: center;
        color: #9ca3af !important; /* light gray text */
        font-size: 0.9rem;
        margin-bottom: 2rem;
        font-family: system-ui, -apple-system, sans-serif;
    }
    
    /* Tabs styling inside modal */
    div[data-testid="stHorizontalBlock"] div[data-testid="column"]:nth-of-type(2) .stTabs [data-baseweb="tab-list"] {
        justify-content: center !important;
        gap: 1.5rem !important;
        border-bottom: 1px solid #2d2a3a !important; /* dark separator */
        margin-bottom: 1.5rem !important;
        background-color: transparent !important;
    }
    div[data-testid="stHorizontalBlock"] div[data-testid="column"]:nth-of-type(2) .stTabs [data-baseweb="tab"] {
        font-weight: 600 !important;
        color: #9ca3af !important;
        padding-bottom: 0.5rem !important;
        background-color: transparent !important;
    }
    div[data-testid="stHorizontalBlock"] div[data-testid="column"]:nth-of-type(2) .stTabs [aria-selected="true"] {
        color: #6366f1 !important;
        border-bottom-color: #6366f1 !important;
    }
    div[data-testid="stHorizontalBlock"] div[data-testid="column"]:nth-of-type(2) .stTabs div[data-baseweb="tab-highlight"] {
        background-color: #6366f1 !important; /* make baseui tab highlight bar purple */
    }
    
    /* Form Label Styling */
    div[data-testid="stHorizontalBlock"] div[data-testid="column"]:nth-of-type(2) label[data-testid="stWidgetLabel"] p {
        color: #e2e8f0 !important; /* light color for dark theme modal */
        font-weight: 600 !important;
        font-size: 0.9rem !important;
    }
    
    /* Form Inputs styling */
    div[data-testid="stForm"] {
        border: none !important;
        padding: 0 !important;
    }
    div[data-testid="stHorizontalBlock"] div[data-testid="column"]:nth-of-type(2) div[data-testid="stTextInput"] div[data-baseweb="input"] {
        background-color: #ffffff !important; /* white input background */
        border: 1px solid #d1d5db !important;
        border-radius: 8px !important;
        height: 46px !important;
        padding: 0 !important;
        display: flex !important;
        align-items: center !important; /* vertically center children (input & eye button) */
        overflow: hidden !important;
        cursor: text !important;
    }
    /* Force all intermediate wrapper divs inside the input container to be transparent and full-height */
    div[data-testid="stHorizontalBlock"] div[data-testid="column"]:nth-of-type(2) div[data-testid="stTextInput"] div[data-baseweb="input"] div {
        background-color: transparent !important;
        border: none !important;
        height: 100% !important;
        display: flex !important;
        align-items: center !important;
        cursor: text !important;
    }
    div[data-testid="stHorizontalBlock"] div[data-testid="column"]:nth-of-type(2) div[data-testid="stTextInput"] div[data-baseweb="input"] input {
        background-color: transparent !important;
        border: none !important;
        color: #1f2937 !important; /* dark text color inside white inputs */
        height: 100% !important;
        padding: 0 1rem !important;
        font-size: 0.95rem !important;
        margin: 0 !important;
        cursor: text !important;
        caret-color: #6366f1 !important; /* custom brand purple cursor color */
    }
    /* Autofill overrides to preserve white background */
    div[data-testid="stHorizontalBlock"] div[data-testid="column"]:nth-of-type(2) div[data-testid="stTextInput"] input:-webkit-autofill,
    div[data-testid="stHorizontalBlock"] div[data-testid="column"]:nth-of-type(2) div[data-testid="stTextInput"] input:-webkit-autofill:hover,
    div[data-testid="stHorizontalBlock"] div[data-testid="column"]:nth-of-type(2) div[data-testid="stTextInput"] input:-webkit-autofill:focus,
    div[data-testid="stHorizontalBlock"] div[data-testid="column"]:nth-of-type(2) div[data-testid="stTextInput"] input:-webkit-autofill:active {
        -webkit-box-shadow: 0 0 0 30px white inset !important;
        -webkit-text-fill-color: #1f2937 !important;
    }
    div[data-testid="stHorizontalBlock"] div[data-testid="column"]:nth-of-type(2) div[data-testid="stTextInput"] div[data-baseweb="input"]:focus-within {
        border-color: #6366f1 !important;
        box-shadow: 0 0 0 2px rgba(99, 102, 241, 0.15) !important;
    }
    div[data-testid="stHorizontalBlock"] div[data-testid="column"]:nth-of-type(2) div[data-testid="stTextInput"] div[data-baseweb="input"] button {
        background-color: transparent !important;
        border: none !important;
        color: #6366f1 !important;
        margin-right: 0.5rem !important;
        box-shadow: none !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        height: 100% !important; /* center eye icon vertically */
    }
    
    /* Button design: Continue (Violet/purple) */
    div[data-testid="stHorizontalBlock"] div[data-testid="column"]:nth-of-type(2) div[data-testid="stFormSubmitButton"] button {
        height: 48px !important;
        background-color: #6366f1 !important;
        color: #ffffff !important;
        font-weight: 600 !important;
        font-size: 1rem !important;
        border: none !important;
        border-radius: 8px !important;
        transition: background-color 0.2s !important;
        box-shadow: 0 4px 6px -1px rgba(99, 102, 241, 0.1) !important;
        margin-top: 1rem !important;
        cursor: pointer !important;
        width: 100% !important;
    }
    div[data-testid="stHorizontalBlock"] div[data-testid="column"]:nth-of-type(2) div[data-testid="stFormSubmitButton"] button:hover {
        background-color: #4f46e5 !important;
    }
    
    /* Links inside modal */
    div[data-testid="stHorizontalBlock"] div[data-testid="column"]:nth-of-type(2) .forgot-password-link button {
        height: auto !important;
        background-color: transparent !important;
        color: #6366f1 !important;
        font-weight: 600 !important;
        font-size: 0.9rem !important;
        border: none !important;
        border-radius: 0 !important;
        box-shadow: none !important;
        margin: 0.75rem auto !important;
        padding: 0 !important;
        cursor: pointer !important;
        display: block !important;
        text-align: center !important;
        width: auto !important;
    }
    div[data-testid="stHorizontalBlock"] div[data-testid="column"]:nth-of-type(2) .forgot-password-link button:hover {
        color: #4f46e5 !important;
        background-color: transparent !important;
        text-decoration: underline !important;
    }
    
    .signup-text-left {
        text-align: right;
        color: #9ca3af !important;
        font-size: 0.9rem;
        line-height: 36px;
    }
    
    div[data-testid="stHorizontalBlock"] div[data-testid="column"]:nth-of-type(2) .signup-link-right button {
        height: 36px !important;
        background-color: transparent !important;
        color: #6366f1 !important;
        font-weight: 600 !important;
        font-size: 0.9rem !important;
        border: none !important;
        border-radius: 0 !important;
        box-shadow: none !important;
        margin: 0 !important;
        padding: 0 !important;
        cursor: pointer !important;
        display: inline-block !important;
        text-align: left !important;
        width: auto !important;
    }
    div[data-testid="stHorizontalBlock"] div[data-testid="column"]:nth-of-type(2) .signup-link-right button:hover {
        color: #4f46e5 !important;
        background-color: transparent !important;
        text-decoration: underline !important;
    }
    
    div[data-testid="stHorizontalBlock"] div[data-testid="column"]:nth-of-type(2) .back-to-login-link button {
        height: auto !important;
        background-color: transparent !important;
        color: #9ca3af !important;
        font-weight: 600 !important;
        font-size: 0.9rem !important;
        border: none !important;
        border-radius: 0 !important;
        box-shadow: none !important;
        margin: 1.5rem auto 0 auto !important;
        padding: 0 !important;
        cursor: pointer !important;
        display: block !important;
        text-align: center !important;
        width: auto !important;
    }
    div[data-testid="stHorizontalBlock"] div[data-testid="column"]:nth-of-type(2) .back-to-login-link button:hover {
        color: #ffffff !important;
        background-color: transparent !important;
    }
    
    .or-text {
        text-align: center;
        color: #9ca3af !important;
        font-size: 0.85rem;
        margin: 1.5rem 0;
        position: relative;
    }
    .or-text::before, .or-text::after {
        content: "";
        position: absolute;
        top: 50%;
        width: 30%;
        height: 1px;
        background: #2d2a3a !important;
    }
    .or-text::before { left: 0; }
    .or-text::after { right: 0; }
    
    /* Google OAuth link button styling (White) */
    div[data-testid="stHorizontalBlock"] div[data-testid="column"]:nth-of-type(2) a[data-testid="stLinkButton"] {
        height: 48px !important;
        background-color: #ffffff !important; /* white background */
        color: #374151 !important; /* dark text */
        border: 1px solid #cbd5e1 !important; /* border */
        border-radius: 8px !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        font-weight: 600 !important;
        text-decoration: none !important;
        box-shadow: none !important;
    }
    div[data-testid="stHorizontalBlock"] div[data-testid="column"]:nth-of-type(2) a[data-testid="stLinkButton"]:hover {
        background-color: #f9fafb !important;
        border-color: #6366f1 !important;
    }
</style>
"""


def _get_redirect_uri():
    return os.getenv("APP_URL", "http://localhost:8501").rstrip("/")


def _google_oauth_configured():
    return bool(os.getenv("GOOGLE_CLIENT_ID") and os.getenv("GOOGLE_CLIENT_SECRET"))


def _get_query_param(key):
    """Read a query parameter (compatible with Streamlit 1.28+)."""
    if hasattr(st, "query_params"):
        return st.query_params.get(key)

    values = st.experimental_get_query_params().get(key, [])
    return values[0] if values else None


def _clear_query_params():
    """Clear URL query parameters after OAuth callback."""
    if hasattr(st, "query_params"):
        st.query_params.clear()
    else:
        st.experimental_set_query_params()


def _create_google_flow():
    redirect_uri = _get_redirect_uri()
    return Flow.from_client_config(
        {
            "web": {
                "client_id": os.getenv("GOOGLE_CLIENT_ID"),
                "client_secret": os.getenv("GOOGLE_CLIENT_SECRET"),
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "redirect_uris": [redirect_uri],
            }
        },
        scopes=[
            "openid",
            "https://www.googleapis.com/auth/userinfo.email",
            "https://www.googleapis.com/auth/userinfo.profile",
        ],
        redirect_uri=redirect_uri,
    )


def handle_google_oauth_callback():
    """Complete Google OAuth if callback query params are present."""
    code = _get_query_param("code")

    if not code or st.session_state.get("authenticated"):
        return

    if not _google_oauth_configured():
        st.error("Google Sign-In is not configured.")
        return

    try:
        flow = _create_google_flow()
        flow.fetch_token(code=code)
        credentials = flow.credentials

        # Get user info from Google's Userinfo API
        user_info_response = requests.get(
            "https://www.googleapis.com/oauth2/v2/userinfo",
            headers={"Authorization": f"Bearer {credentials.token}"}
        )
        user_info_response.raise_for_status()
        user_info = user_info_response.json()

        email = user_info.get("email")
        name = user_info.get("name") or email.split("@")[0]
        google_id = user_info.get("id") or user_info.get("sub")

        # Create or retrieve user document in MongoDB
        user = get_or_create_google_user(email=email, name=name, google_id=google_id)

        # Set user session state
        st.session_state.authenticated = True
        st.session_state.user = user
        st.session_state.credentials = credentials

        from modules.auth_db import create_user_session
        session_token = create_user_session(user["id"])
        if session_token:
            st.session_state.session_token = session_token
            js_code = (
                f"try {{"
                f"localStorage.setItem('session_token', '{session_token}');"
                f"localStorage.setItem('page', 'upload');"
                f"setTimeout(function() {{"
                f"window.location.search = '?session_token={session_token}&page=upload';"
                f"}}, 100);"
                f"}} catch(e) {{ console.error(e); }}"
            )
            st.markdown(f'<img src="x" onerror="{js_code}" style="display:none;"/>', unsafe_allow_html=True)
            st.stop()
        else:
            _clear_query_params()
            st.rerun()

    except Exception as error:
        st.error(f"Google Sign-In failed: {error}")


def _send_otp_email(email, otp):
    """Send OTP email if SMTP is configured, otherwise fallback to console logging."""
    smtp_server = os.getenv("SMTP_SERVER")
    smtp_port = os.getenv("SMTP_PORT", "587")
    smtp_username = os.getenv("SMTP_USERNAME") or os.getenv("SENDER_EMAIL")
    smtp_password = os.getenv("SMTP_PASSWORD") or os.getenv("SENDER_PASSWORD")
    if smtp_password and len(smtp_password.replace(" ", "")) == 16:
        smtp_password = smtp_password.replace(" ", "")
    smtp_from = os.getenv("SMTP_FROM") or os.getenv("SENDER_EMAIL") or smtp_username

    subject = "AcademicAnalyzer Password Reset OTP"
    body = f"""Hello,

You requested a password reset for your AcademicAnalyzer account.
Your 6-digit One-Time Password (OTP) is:

👉 {otp} 👈

This code is valid for 5 minutes. If you did not request this reset, please ignore this email.

Best regards,
AcademicAnalyzer Team
"""

    if not smtp_server or not smtp_username or not smtp_password:
        # SMTP not configured
        print(f"[AcademicAnalyzer Reset OTP] To: {email} | OTP: {otp}")
        return False, "SMTP server not configured. OTP printed to terminal."

    try:
        msg = MIMEText(body)
        msg["Subject"] = subject
        msg["From"] = smtp_from
        msg["To"] = email

        with smtplib.SMTP(smtp_server, int(smtp_port)) as server:
            server.starttls()
            server.login(smtp_username, smtp_password)
            server.sendmail(smtp_from, [email], msg.as_string())
        
        return True, "OTP email sent successfully!"
    except Exception as e:
        print(f"[AcademicAnalyzer SMTP Error] Failed to send email: {e}")
        return False, f"Failed to send email: {e}"


def render_auth_page():
    """Render login, signup, forgot password, and OTP verification pages."""
    init_db()
    st.markdown(AUTH_CSS, unsafe_allow_html=True)

    # 1. Render Outer Branding Logo & Title
    st.markdown("""
    <div class="auth-outer-header">
        <div class="auth-outer-logo">
            <svg viewBox="0 0 48 48" style="width: 48px; height: 48px;">
                <rect x="4" y="4" width="40" height="34" rx="10" fill="#6366f1"/>
                <path d="M12 38 L12 44 L18 38 Z" fill="#6366f1"/>
                <path d="M24 12 L36 18 L24 24 L12 18 Z" fill="#ffffff"/>
                <path d="M18 21 L18 27 C18 30, 30 30, 30 27 L30 21" fill="none" stroke="#ffffff" stroke-width="2" stroke-linecap="round"/>
                <path d="M33 19.5 L33 26" fill="none" stroke="#ffffff" stroke-width="1.5"/>
                <circle cx="33" cy="26" r="1.5" fill="#ffffff"/>
            </svg>
        </div>
        <div class="auth-outer-text">
            <div class="auth-outer-title">AcademicAnalyzer</div>
            <div class="auth-outer-subtitle">Learn Smarter. Score Better.</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 2. Render Dummy Dashboard Background Container
    st.markdown("""
    <div class="auth-main-wrapper">
        <!-- Sidebar -->
        <div class="auth-sidebar">
            <div class="auth-sidebar-logo">
                <svg viewBox="0 0 48 48" style="width: 32px; height: 32px; vertical-align: middle;">
                    <rect x="4" y="4" width="40" height="34" rx="10" fill="#6366f1"/>
                    <path d="M12 38 L12 44 L18 38 Z" fill="#6366f1"/>
                    <path d="M24 12 L36 18 L24 24 L12 18 Z" fill="#ffffff"/>
                    <path d="M18 21 L18 27 C18 30, 30 30, 30 27 L30 21" fill="none" stroke="#ffffff" stroke-width="2" stroke-linecap="round"/>
                    <path d="M33 19.5 L33 26" fill="none" stroke="#ffffff" stroke-width="1.5"/>
                    <circle cx="33" cy="26" r="1.5" fill="#ffffff"/>
                </svg>
                <span style="font-weight: 700; font-size: 1.1rem; color: #4f46e5; margin-left: 0.5rem;">AcademicAnalyzer</span>
            </div>
            <div class="auth-sidebar-menu">
                <div class="auth-menu-item active">
                    <span class="auth-menu-icon">🏠</span> Dashboard
                </div>
                <div class="auth-menu-item">
                    <span class="auth-menu-icon">📄</span> My PDFs
                </div>
                <div class="auth-menu-item">
                    <span class="auth-menu-icon">🧠</span> Summaries
                </div>
                <div class="auth-menu-item">
                    <span class="auth-menu-icon">❓</span> Quiz
                </div>
                <div class="auth-menu-item">
                    <span class="auth-menu-icon">📊</span> Analytics
                </div>
                <div class="auth-menu-item">
                    <span class="auth-menu-icon">📅</span> Study Plan
                </div>
                <div class="auth-menu-item">
                    <span class="auth-menu-icon">⚙️</span> Settings
                </div>
            </div>
        </div>
        
        <!-- Main Pane -->
        <div class="auth-main-pane">
            <!-- Navbar -->
            <div class="auth-navbar">
                <div class="auth-nav-tabs">
                    <span class="auth-nav-tab active">Dashboard</span>
                    <span class="auth-nav-tab">PDFs</span>
                    <span class="auth-nav-tab">Quiz</span>
                    <span class="auth-nav-tab">Analytics</span>
                    <span class="auth-nav-tab">Settings</span>
                </div>
                <div class="auth-avatar">U</div>
            </div>
            
            <!-- Scroll Content -->
            <div class="auth-dashboard-content">
                <div class="auth-grid-row">
                    <!-- Left Column -->
                    <div class="auth-col-left">
                        <!-- Welcome Card -->
                        <div class="auth-card-welcome">
                            <h3>Welcome Back! 👋</h3>
                            <p>Upload your notes, learn and test yourself with AI-powered insights.</p>
                        </div>
                        <!-- Recent PDFs -->
                        <div class="auth-card-recent">
                            <div class="auth-card-header">Recent PDFs</div>
                            <div class="auth-pdf-list">
                                <div class="auth-pdf-item">
                                    <span class="auth-pdf-icon">📄</span>
                                    <div class="auth-pdf-info">
                                        <div class="auth-pdf-name">Cloud Computing.pdf</div>
                                        <div class="auth-pdf-meta">Uploaded 2 days ago</div>
                                    </div>
                                </div>
                                <div class="auth-pdf-item">
                                    <span class="auth-pdf-icon">📄</span>
                                    <div class="auth-pdf-info">
                                        <div class="auth-pdf-name">Operating Systems.pdf</div>
                                        <div class="auth-pdf-meta">Uploaded 5 days ago</div>
                                    </div>
                                </div>
                                <div class="auth-pdf-item">
                                    <span class="auth-pdf-icon">📄</span>
                                    <div class="auth-pdf-info">
                                        <div class="auth-pdf-name">DBMS Notes.pdf</div>
                                        <div class="auth-pdf-meta">Uploaded 1 week ago</div>
                                    </div>
                                </div>
                                <div class="auth-pdf-item">
                                    <span class="auth-pdf-icon">📄</span>
                                    <div class="auth-pdf-info">
                                        <div class="auth-pdf-name">Machine Learning.pdf</div>
                                        <div class="auth-pdf-meta">Uploaded 1 week ago</div>
                                    </div>
                                </div>
                            </div>
                            <div class="auth-view-all-link">View all PDFs →</div>
                        </div>
                    </div>
                    
                    <!-- Right Column -->
                    <div class="auth-col-right">
                        <!-- Stats Grid -->
                        <div class="auth-stats-grid">
                            <div class="auth-stat-card">
                                <div class="auth-stat-icon" style="background-color: #eef2ff; color: #6366f1;">📄</div>
                                <div class="auth-stat-details">
                                    <div class="auth-stat-num">12</div>
                                    <div class="auth-stat-label">PDFs Uploaded</div>
                                </div>
                            </div>
                            <div class="auth-stat-card">
                                <div class="auth-stat-icon" style="background-color: #ecfdf5; color: #10b981;">🧠</div>
                                <div class="auth-stat-details">
                                    <div class="auth-stat-num">8</div>
                                    <div class="auth-stat-label">Summaries Generated</div>
                                </div>
                            </div>
                            <div class="auth-stat-card">
                                <div class="auth-stat-icon" style="background-color: #fffbe6; color: #d4b106;">❓</div>
                                <div class="auth-stat-details">
                                    <div class="auth-stat-num">85%</div>
                                    <div class="auth-stat-label">Average Score</div>
                                </div>
                            </div>
                            <div class="auth-stat-card">
                                <div class="auth-stat-icon" style="background-color: #fdf2f8; color: #ec4899;">👤</div>
                                <div class="auth-stat-details">
                                    <div class="auth-stat-num">6</div>
                                    <div class="auth-stat-label">Quizzes Attempted</div>
                                </div>
                            </div>
                        </div>
                        
                        <!-- Your Progress Card -->
                        <div class="auth-card-progress">
                            <div class="auth-card-header">Your Progress</div>
                            <div class="auth-chart-container">
                                <svg viewBox="0 0 400 120" style="width: 100%; height: 100px;">
                                    <defs>
                                        <linearGradient id="chart-grad" x1="0" y1="0" x2="0" y2="1">
                                            <stop offset="0%" stop-color="#6366f1" stop-opacity="0.2"/>
                                            <stop offset="100%" stop-color="#6366f1" stop-opacity="0"/>
                                        </linearGradient>
                                    </defs>
                                    <line x1="0" y1="100" x2="400" y2="100" stroke="#f1f5f9" stroke-width="1"/>
                                    <line x1="0" y1="60" x2="400" y2="60" stroke="#f1f5f9" stroke-width="1"/>
                                    <line x1="0" y1="20" x2="400" y2="20" stroke="#f1f5f9" stroke-width="1"/>
                                    
                                    <path d="M 10 90 L 60 70 L 115 50 L 170 55 L 225 35 L 280 42 L 335 25 L 390 15 L 390 120 L 10 120 Z" fill="url(#chart-grad)"/>
                                    <path d="M 10 90 L 60 70 L 115 50 L 170 55 L 225 35 L 280 42 L 335 25 L 390 15" fill="none" stroke="#6366f1" stroke-width="3" stroke-linecap="round"/>
                                    
                                    <circle cx="10" cy="90" r="4" fill="#6366f1"/>
                                    <circle cx="60" cy="70" r="4" fill="#6366f1"/>
                                    <circle cx="115" cy="50" r="4" fill="#6366f1"/>
                                    <circle cx="170" cy="55" r="4" fill="#6366f1"/>
                                    <circle cx="225" cy="35" r="4" fill="#6366f1"/>
                                    <circle cx="280" cy="42" r="4" fill="#6366f1"/>
                                    <circle cx="335" cy="25" r="4" fill="#6366f1"/>
                                    <circle cx="390" cy="15" r="4" fill="#6366f1"/>
                                </svg>
                                <div class="auth-chart-labels">
                                    <span>Mon</span>
                                    <span>Tue</span>
                                    <span>Wed</span>
                                    <span>Thu</span>
                                    <span>Fri</span>
                                    <span>Sat</span>
                                    <span>Sun</span>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                
                <!-- Bottom section: AI Features -->
                <div class="auth-features-section">
                    <div class="auth-section-title">AI Features</div>
                    <div class="auth-features-grid">
                        <div class="auth-feature-card">
                            <span class="auth-feature-icon" style="background-color: #f5f3ff; color: #8b5cf6;">📄</span>
                            <div class="auth-feature-name">Smart Summary</div>
                            <div class="auth-feature-desc">Get concise summaries of your PDFs</div>
                        </div>
                        <div class="auth-feature-card">
                            <span class="auth-feature-icon" style="background-color: #ecfdf5; color: #10b981;">🧠</span>
                            <div class="auth-feature-name">Important Topics</div>
                            <div class="auth-feature-desc">Extract important topics automatically</div>
                        </div>
                        <div class="auth-feature-card">
                            <span class="auth-feature-icon" style="background-color: #eff6ff; color: #3b82f6;">❓</span>
                            <div class="auth-feature-name">AI Quiz Generator</div>
                            <div class="auth-feature-desc">Generate quizzes from your content</div>
                        </div>
                        <div class="auth-feature-card">
                            <span class="auth-feature-icon" style="background-color: #fff7ed; color: #f97316;">📊</span>
                            <div class="auth-feature-name">Performance Analysis</div>
                            <div class="auth-feature-desc">Analyze your mistakes and improve</div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 3. Render Blur Overlay
    st.markdown('<div class="auth-overlay-blur"></div>', unsafe_allow_html=True)

    # 4. Render Auth Modals based on auth_mode
    _, center, _ = st.columns([1, 1.5, 1])

    if "auth_mode" not in st.session_state:
        st.session_state.auth_mode = "login"

    mode = st.session_state.auth_mode

    with center:
        if mode == "login":
            st.markdown('<div class="auth-title">Sign In to <span>AcademicAnalyzer</span></div>', unsafe_allow_html=True)
            st.markdown(
                '<div class="auth-subtitle">Access your dashboard and continue learning.</div>',
                unsafe_allow_html=True,
            )

            with st.form("login_form"):
                email = st.text_input("Email Address", placeholder="📧 name@email.com")
                password = st.text_input("Password", type="password", placeholder="🔒 Enter your password  👁")
                submitted = st.form_submit_button("Continue", type="primary", use_container_width=True)

            if submitted:
                if not email or not password:
                    st.error("Please enter email and password.")
                else:
                    success, user, message = authenticate_user(email, password)
                    if success:
                        st.session_state.authenticated = True
                        st.session_state.user = user
                        
                        from modules.auth_db import create_user_session
                        session_token = create_user_session(user["id"])
                        if session_token:
                            st.session_state.session_token = session_token
                            js_code = (
                                f"try {{"
                                f"localStorage.setItem('session_token', '{session_token}');"
                                f"localStorage.setItem('page', 'upload');"
                                f"setTimeout(function() {{"
                                f"window.location.search = '?session_token={session_token}&page=upload';"
                                f"}}, 100);"
                                f"}} catch(e) {{ console.error(e); }}"
                            )
                            st.markdown(f'<img src="x" onerror="{js_code}" style="display:none;"/>', unsafe_allow_html=True)
                            st.stop()
                        else:
                            st.success(message)
                            st.rerun()
                    else:
                        st.error(message)

            # Forgot Password link styled as link button
            st.markdown('<div class="forgot-password-link">', unsafe_allow_html=True)
            if st.button("Forgot password?", key="forgot_pwd_btn"):
                st.session_state.auth_mode = "forgot_password"
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

            # "Don't have an account? Sign Up" helper text
            col1, col2 = st.columns([3.2, 1.8])
            with col1:
                st.markdown('<div class="signup-text-left">Don\'t have an account?</div>', unsafe_allow_html=True)
            with col2:
                st.markdown('<div class="signup-link-right">', unsafe_allow_html=True)
                if st.button("Sign Up", key="signup_link_btn"):
                    st.session_state.auth_mode = "signup"
                    st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)

            st.markdown('<div class="or-text">Or continue with</div>', unsafe_allow_html=True)
            
            if _google_oauth_configured():
                flow = _create_google_flow()
                auth_url, _ = flow.authorization_url(
                    access_type="offline",
                    include_granted_scopes="true",
                    prompt="select_account",
                    )
                st.link_button("Continue with Google", auth_url, use_container_width=True)
            else:
                st.caption(
                    "To enable Google Sign-In, add GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, "
                    "and APP_URL to your .env file."
                )

        elif mode == "signup":
            st.markdown('<div class="auth-title">Create Account</div>', unsafe_allow_html=True)
            st.markdown(
                '<div class="auth-subtitle">Join AcademicAnalyzer and start learning.</div>',
                unsafe_allow_html=True,
            )

            with st.form("signup_form"):
                name = st.text_input("Full Name", placeholder="👤 Your name")
                email = st.text_input("Email Address", placeholder="📧 name@email.com")
                password = st.text_input("Password", type="password", placeholder="🔒 Choose password  👁")
                confirm_password = st.text_input("Confirm Password", type="password", placeholder="🔒 Confirm password")
                submitted = st.form_submit_button("Create Account", type="primary", use_container_width=True)

            if submitted:
                if not all([name, email, password, confirm_password]):
                    st.error("Please fill in all fields.")
                elif password != confirm_password:
                    st.error("Passwords do not match.")
                elif len(password) < 6:
                    st.error("Password must be at least 6 characters.")
                else:
                    success, message = create_user(email, name, password)
                    if success:
                        st.success(message + " You can now log in.")
                        st.session_state.auth_mode = "login"
                        st.rerun()
                    else:
                        st.error(message)

            col1, col2 = st.columns([3.2, 1.8])
            with col1:
                st.markdown('<div class="signup-text-left">Already have an account?</div>', unsafe_allow_html=True)
            with col2:
                st.markdown('<div class="signup-link-right">', unsafe_allow_html=True)
                if st.button("Login", key="login_link_btn"):
                    st.session_state.auth_mode = "login"
                    st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)

        elif mode == "forgot_password":
            st.markdown('<div class="auth-title">Reset Password</div>', unsafe_allow_html=True)
            st.markdown(
                '<div class="auth-subtitle">Enter your registered email to receive an OTP.</div>',
                unsafe_allow_html=True,
            )

            with st.form("forgot_form"):
                email = st.text_input("Email Address", placeholder="📧 name@email.com")
                submitted = st.form_submit_button("Send OTP", type="primary", use_container_width=True)

            if submitted:
                if not email:
                    st.error("Please enter your email address.")
                elif not user_exists(email):
                    st.error("No account with this email address exists.")
                else:
                    # Generate OTP and store in session state
                    otp = "".join(str(random.randint(0, 9)) for _ in range(6))
                    st.session_state.reset_email = email
                    st.session_state.reset_otp = otp
                    st.session_state.otp_timestamp = time.time()
                    
                    # Send OTP email
                    sent, msg = _send_otp_email(email, otp)
                    if sent:
                        st.success(msg)
                        st.session_state.auth_mode = "verify_otp"
                        st.rerun()
                    else:
                        st.error(f"Failed to send OTP email: {msg}")

            st.markdown('<div class="back-to-login-link">', unsafe_allow_html=True)
            if st.button("← Back to Login", key="back_to_login_btn"):
                st.session_state.auth_mode = "login"
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

        elif mode == "verify_otp":
            st.markdown('<div class="auth-title">Verify OTP</div>', unsafe_allow_html=True)
            st.markdown(
                f'<div class="auth-subtitle">Enter the code sent to {st.session_state.get("reset_email")}.</div>',
                unsafe_allow_html=True,
            )

            # In development mode (SMTP server not set), show OTP in an info box
            smtp_server = os.getenv("SMTP_SERVER")
            smtp_password = os.getenv("SMTP_PASSWORD") or os.getenv("SENDER_PASSWORD")
            if not smtp_server or not smtp_password:
                st.info(f"🔑 **Dev Mode OTP**: `{st.session_state.get('reset_otp')}`")

            with st.form("verify_otp_form"):
                otp_input = st.text_input("One-Time Password (OTP)", placeholder="🔢 Enter 6-digit code")
                new_password = st.text_input("New Password", type="password", placeholder="🔒 Choose new password")
                confirm_password = st.text_input("Confirm New Password", type="password", placeholder="🔒 Confirm new password")
                submitted = st.form_submit_button("Reset Password", type="primary", use_container_width=True)

            if submitted:
                # Validation checks
                if not all([otp_input, new_password, confirm_password]):
                    st.error("Please fill in all fields.")
                elif otp_input.strip() != st.session_state.get("reset_otp"):
                    st.error("Invalid OTP code. Please try again.")
                elif time.time() - st.session_state.get("otp_timestamp", 0) > 300:
                    st.error("OTP has expired (valid for 5 minutes). Please request a new one.")
                elif new_password != confirm_password:
                    st.error("Passwords do not match.")
                elif len(new_password) < 6:
                    st.error("Password must be at least 6 characters.")
                else:
                    success, msg = reset_user_password(st.session_state.get("reset_email"), new_password)
                    if success:
                        st.success(msg)
                        st.session_state.auth_mode = "login"
                        # Clean up reset data
                        for key in ["reset_otp", "reset_email", "otp_timestamp"]:
                            if key in st.session_state:
                                del st.session_state[key]
                        st.rerun()
                    else:
                        st.error(msg)

            st.markdown('<div class="back-to-login-link">', unsafe_allow_html=True)
            if st.button("← Back to Login", key="back_to_login_btn2"):
                st.session_state.auth_mode = "login"
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)


def logout_user():
    """Clear authentication state."""
    # Delete session token from DB if it exists
    user = st.session_state.get("user")
    if user and "id" in user:
        try:
            from modules.auth_db import delete_user_session
            delete_user_session(user["id"])
        except Exception as e:
            print(f"Error deleting session on logout: {e}")
            
    for key in ["authenticated", "user", "session_token"]:
        if key in st.session_state:
            del st.session_state[key]
            
    st.session_state.logged_out = True
