import streamlit as st
import numpy as np
from PIL import Image

def load_css():
    """Inject custom CSS for Portfolio Polish."""
    st.markdown("""
    <style>
        /* Global Font & Theme overrides */
        @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&family=Inter:wght@300;400;600&display=swap');
        
        html, body, [class*="css"]  {
            font-family: 'Inter', sans-serif;
        }
        .stCode, .stMarkdown code {
            font-family: 'JetBrains Mono', monospace !important;
        }

        /* Sidebar Styling */
        [data-testid="stSidebar"] {
            background-color: #0e1117;
            border-right: 1px solid #262730;
        }
        
        /* Headers */
        h1, h2, h3 {
            font-weight: 600;
            letter-spacing: -0.5px;
        }
        
        /* Metrics */
        [data-testid="stMetricValue"] {
            font-family: 'JetBrains Mono', monospace;
            color: #00ff41; /* Cyberpunk Green */
        }

        /* Custom Buttons - Primary */
        .stButton button[kind="primary"] {
            background: linear-gradient(90deg, #4f46e5 0%, #7c3aed 100%);
            border: none;
            transition: all 0.2s ease;
        }
        .stButton button[kind="primary"]:hover {
            transform: scale(1.02);
            box-shadow: 0 4px 12px rgba(124, 58, 237, 0.3);
        }
        
        /* Expander styling */
        .streamlit-expanderHeader {
            font-weight: 500;
            color: #a1a1aa;
        }
    </style>
    """, unsafe_allow_html=True)

@st.cache_data
def convert_to_rgb(image_file):
    """
    Convert uploaded image file to RGB numpy array. Cached.
    
    [CONFIG] VPS SAFETY LIMIT: Change `max_dim` below to 4096+ for local/high-end use.
    Currently set to 1024px to prevent crashes on VPS.
    """
    try:
        image = Image.open(image_file).convert('RGB')
        
        max_dim = 1024
        if image.width > max_dim or image.height > max_dim:
            image.thumbnail((max_dim, max_dim), Image.LANCZOS)
            
        return np.array(image), image
    except Exception:
        return None, None
