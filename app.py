import streamlit as st
import numpy as np
import os
import glob
from core.utils import load_css, convert_to_rgb
from core.navigation import make_sidebar

st.set_page_config(
    page_title="The AI Deception Toolkit",
    page_icon="🎭",
    layout="wide",
    initial_sidebar_state="expanded",
)

def main():
    make_sidebar()
    load_css()
    
    # Sidebar: Title & Info (REMOVED - handled by make_sidebar)
    # with st.sidebar: ...

    # Main Area: Welcome Screen
    st.markdown(
        """
<div style='text-align: center; padding: 40px;'>
<h1>The AI Deception Toolkit</h1>
<p style='color: #9ca3af; font-size: 1.1em; max-width: 800px; margin: 0 auto 30px auto;'>
A companion tool for the blog post: <i>"How to Trick AI Detectors."</i><br>
This interactive demo shows how easily detectors can be tricked by basic image manipulation.
</p>
<div style='display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; text-align: left;'>
<div style='padding: 20px; background: #1e1e24; border-radius: 12px; border: 1px solid #2d2d3a;'>
<h3 style='color: #00ff41; margin-top: 0;'>📊 The Scanner</h3>
<p style='font-size: 0.9em; color: #a1a1aa; line-height: 1.5;'>
<b>What it does:</b> Visualizes the "invisible" noise.<br>
Inspect the patterns and waves of the image to understand how they work.
</p>
</div>
<div style='padding: 20px; background: #1e1e24; border-radius: 12px; border: 1px solid #2d2d3a;'>
<h3 style='color: #a78bfa; margin-top: 0;'>📷 The Humanizer</h3>
<p style='font-size: 0.9em; color: #a1a1aa; line-height: 1.5;'>
<b>The Goal:</b> Evade Detection.<br>
Covers the AI patterns with real noise and grain.
</p>
</div>
<div style='padding: 20px; background: #1e1e24; border-radius: 12px; border: 1px solid #2d2d3a;'>
<h3 style='color: #f472b6; margin-top: 0;'>🎭 The Faker</h3>
<p style='font-size: 0.9em; color: #a1a1aa; line-height: 1.5;'>
<b>The Goal:</b> Trigger False Positives.<br>
Injects AI patterns into a real photo.
</p>
</div>
</div>
</div>
        """,
        unsafe_allow_html=True,
    )

    st.divider()

    # Upload Section
    st.subheader("📤 Upload Image")
    uploaded_file = st.file_uploader(
        "Choose a file (Max 200MB)", type=["jpg", "jpeg", "png"]
    )
    if uploaded_file:
        # Process & Redirect
        with st.spinner("Processing..."):
            file_signature = f"{uploaded_file.name}-{uploaded_file.size}"
            
            # Check if it's a new file to reset downstream state
            if st.session_state.get("last_uploaded_file") != file_signature:
                st.session_state.processed_image = None
                st.session_state.processing_type = None
                st.session_state.last_uploaded_file = file_signature
                st.session_state.toast_shown_id = None # Reset toast
            
            original_array, _, was_resized = convert_to_rgb(uploaded_file)
            
            if was_resized and st.session_state.get("toast_shown_id") != file_signature:
                    st.toast("High-Res Image detected. Optimized to 1024px for stability.", icon="⚠️")
                    st.session_state.toast_shown_id = file_signature

            # Persist to Session State
            st.session_state.original_array = original_array
            st.session_state.input_filename = os.path.splitext(uploaded_file.name)[0]
            # Store object reference
            st.session_state.uploaded_file_obj = uploaded_file 

        st.success("Image Loaded!")
        st.switch_page("pages/scanner.py")

    st.divider()

    st.subheader("🖼️ or Choose Sample")
    ai_samples = sorted(glob.glob("assets/ai/*.*"))
    real_samples = sorted(glob.glob("assets/real/*.*"))
    
    all_samples = ai_samples + real_samples
    if not all_samples:
            st.info("No samples found.")
    else:
            cols = st.columns(4)
            for i, path in enumerate(all_samples[:4]):
                with cols[i % 4]:
                    st.image(path, width=300) # Adjusted width for 4-col layout
                    
                    c_btn, c_lbl = st.columns([1, 2])
                    with c_btn:
                        load_clicked = st.button("Load", key=f"smp_{path}")
                    with c_lbl:
                        if "assets/ai" in path:
                            st.markdown("**AI Generated**")
                        else:
                            st.markdown("**Real Photo**")

                    if load_clicked:
                        st.session_state.selected_sample = path
                        original_array, _, was_resized = convert_to_rgb(path)
                        
                        if was_resized:
                            st.toast("High-Res Sample optimized.", icon="⚠️")
                            
                        st.session_state.original_array = original_array
                        st.session_state.input_filename = os.path.splitext(os.path.basename(path))[0]
                        st.switch_page("pages/scanner.py")


if __name__ == "__main__":
    main()
