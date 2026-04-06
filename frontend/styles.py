import streamlit as st

def apply_custom_styles():
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

        :root {
            --bg-primary: #09090b;
            --bg-secondary: #18181b;
            --bg-tertiary: #27272a;
            --accent-blue: #3b82f6;
            --accent-emerald: #10b981;
            --text-primary: #fafafa;
            --text-secondary: #a1a1aa;
            --border-color: #27272a;
            --glass-bg: rgba(24, 24, 27, 0.7);
            --glass-border: rgba(63, 63, 70, 0.4);
        }

        /* Global Styles */
        .stApp {
            background-color: var(--bg-primary);
            color: var(--text-primary);
            font-family: 'Inter', sans-serif;
        }

        /* Top Gradient Border */
        .stApp::before {
            content: "";
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            height: 4px;
            background: linear-gradient(90deg, var(--accent-blue), var(--accent-emerald));
            z-index: 9999;
        }

        /* Sidebar Styling */
        [data-testid="stSidebar"] {
            background-color: var(--bg-secondary);
            border-right: 1px solid var(--border-color);
        }

        [data-testid="stSidebar"] .stMarkdown {
            padding-top: 1rem;
        }

        /* Glassmorphism Cards */
        .glass-card {
            background: var(--glass-bg);
            backdrop-filter: blur(12px);
            -webkit-backdrop-filter: blur(12px);
            border: 1px solid var(--glass-border);
            border-radius: 12px;
            padding: 1.5rem;
            margin-bottom: 1rem;
            transition: transform 0.2s ease, border-color 0.2s ease;
        }

        .glass-card:hover {
            border-color: var(--accent-blue);
            transform: translateY(-2px);
        }

        /* Buttons */
        .stButton > button {
            background-color: var(--bg-tertiary);
            color: var(--text-primary);
            border: 1px solid var(--border-color);
            border-radius: 6px;
            padding: 0.5rem 1rem;
            font-weight: 500;
            transition: all 0.2s ease;
            width: 100%;
        }

        .stButton > button:hover {
            border-color: var(--accent-blue);
            background-color: var(--bg-secondary);
            color: var(--accent-blue);
            box-shadow: 0 0 15px rgba(59, 130, 246, 0.1);
        }

        /* Metrics */
        [data-testid="stMetric"] {
            background: var(--bg-secondary);
            border: 1px solid var(--border-color);
            padding: 1rem;
            border-radius: 8px;
        }

        [data-testid="stMetricLabel"] {
            color: var(--text-secondary) !important;
            font-size: 0.875rem !important;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }

        [data-testid="stMetricValue"] {
            color: var(--text-primary) !important;
            font-weight: 600 !important;
        }

        /* Tabs */
        .stTabs [data-baseweb="tab-list"] {
            gap: 8px;
            background-color: transparent;
        }

        .stTabs [data-baseweb="tab"] {
            height: 40px;
            background-color: var(--bg-secondary);
            border-radius: 6px 6px 0 0;
            padding: 0 16px;
            color: var(--text-secondary);
            border: 1px solid var(--border-color);
            border-bottom: none;
        }

        .stTabs [aria-selected="true"] {
            background-color: var(--bg-tertiary) !important;
            color: var(--accent-blue) !important;
            border-color: var(--accent-blue) !important;
        }

        /* Inputs */
        .stTextInput > div > div > input, .stSelectbox > div > div > div {
            background-color: var(--bg-secondary) !important;
            color: var(--text-primary) !important;
            border: 1px solid var(--border-color) !important;
            border-radius: 6px !important;
        }

        /* Code Blocks */
        code {
            font-family: 'JetBrains Mono', monospace !important;
            background-color: var(--bg-secondary) !important;
            color: var(--accent-emerald) !important;
            padding: 0.2rem 0.4rem !important;
            border-radius: 4px !important;
        }

        /* Status Indicators */
        .status-indicator {
            display: inline-block;
            width: 8px;
            height: 8px;
            border-radius: 50%;
            margin-right: 8px;
        }
        .status-online { background-color: var(--accent-emerald); box-shadow: 0 0 8px var(--accent-emerald); }
        .status-offline { background-color: #ef4444; }

        /* Custom Header */
        .header-container {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 1rem 0;
            border-bottom: 1px solid var(--border-color);
            margin-bottom: 2rem;
        }

        .header-title {
            font-size: 1.5rem;
            font-weight: 700;
            letter-spacing: -0.025em;
        }

        .header-badge {
            background: rgba(59, 130, 246, 0.1);
            color: var(--accent-blue);
            padding: 2px 8px;
            border-radius: 4px;
            font-size: 0.75rem;
            font-weight: 600;
            border: 1px solid rgba(59, 130, 246, 0.2);
        }
        </style>
    """, unsafe_allow_html=True)

def glass_card(content, title=None):
    title_html = f"<h3 style='margin-top:0; font-size:1.1rem; color:var(--text-primary);'>{title}</h3>" if title else ""
    st.markdown(f"""
        <div class="glass-card">
            {title_html}
            {content}
        </div>
    """, unsafe_allow_html=True)

def render_header(title, badge_text="v1.0.0"):
    st.markdown(f"""
        <div class="header-container">
            <div class="header-title">{title}</div>
            <div class="header-badge">{badge_text}</div>
        </div>
    """, unsafe_allow_html=True)

def render_status(label, online=True):
    status_class = "status-online" if online else "status-offline"
    st.markdown(f"""
        <div style="display: flex; align-items: center; margin-bottom: 0.5rem;">
            <span class="status-indicator {status_class}"></span>
            <span style="color: var(--text-secondary); font-size: 0.875rem;">{label}</span>
        </div>
    """, unsafe_allow_html=True)

