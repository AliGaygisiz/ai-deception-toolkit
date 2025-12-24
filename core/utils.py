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
    
    [CONFIG] High-Performance Mode (Main Branch).
    Settings unlocked for local/dedicated hardware. 
    Switch to 'deploy-vps' branch for 512MB RAM safety limits.
    """
    try:
        image = Image.open(image_file).convert('RGB')
        
        max_dim = 4096
        was_resized = False
        if image.width > max_dim or image.height > max_dim:
            was_resized = True
            image.thumbnail((max_dim, max_dim), Image.LANCZOS)
            
        return np.array(image), image, was_resized
    except Exception:
        return None, None, False
