"""
Toonify - Streamlit Frontend Application
AI-Powered Image Transformation & Cartoon Recognition
"""
import streamlit as st
from styles import apply_custom_styles
from utils import init_session_state
from views import render_auth_page, render_main_app

# ============ PAGE CONFIG ============
st.set_page_config(
    page_title="Toonify | AI Image Transformation",
    page_icon="🎨",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://github.com/toonify/help',
        'Report a bug': 'https://github.com/toonify/issues',
        'About': """
        # 🎨 Toonify
        
        **AI-Powered Image Transformation & Cartoon Recognition**
        
        Transform your photos into stunning cartoon art with deep learning.
        Identify celebrities in cartoon images with 100-class classification.
        
        ---
        Built with ❤️ using FastAPI + Streamlit + PyTorch
        """
    }
)

# ============ INITIALIZATION ============
apply_custom_styles()
init_session_state()

# ============ MAIN APP ============
def main():
    """Main application entry point."""
    if not st.session_state.authenticated:
        render_auth_page()
    else:
        render_main_app()


if __name__ == "__main__":
    main()
