import streamlit as st
import pandas as pd
from core.utils import load_css
from core.navigation import make_sidebar
from core.analyzer import compute_fft, plot_2d_spectrum, plot_3d_spectrum
from core.metadata import extract_exif

st.set_page_config(
    page_title="The Scanner - AI Deception Toolkit",
    page_icon="📊",
    layout="wide"
)

# Initialize
make_sidebar()
load_css()

st.header("The Scanner: Spectral Analysis")

# State Check
if "original_array" not in st.session_state or st.session_state.original_array is None:
    st.warning("⚠️ No image loaded. Please upload an image on the Home page.")
    st.page_link("app.py", label="Go to Home", icon="🏠")
    st.stop()

original_array = st.session_state.original_array
uploaded_file = st.session_state.get("uploaded_file_obj") # Store object if possible, or handle name

mag_spec, _ = compute_fft(original_array)

# Bento Grid Layout

# Row 1: Image | 3D Topology
r1c1, r1c2 = st.columns(2)
with r1c1:
    st.subheader("Source Image")
    st.image(
        original_array,
        width="stretch",
        caption=f"Resolution: {original_array.shape[1]}x{original_array.shape[0]}",
    )
with r1c2:
    st.subheader("3D Topology (Noise)")
    st.plotly_chart(plot_3d_spectrum(mag_spec))

st.divider()

# Row 2: Frequency Map | EXIF Data
r2c1, r2c2 = st.columns(2)
with r2c1:
    st.subheader("Frequency Map")
    st.pyplot(plot_2d_spectrum(mag_spec))
    st.info(
        "💡 **Bright stars** or **grid patterns** in the spectrum usually indicate AI generation."
    )
with r2c2:
    st.subheader("EXIF Data")
    # Get EXIF data from source
    # We might need to store the raw bytes or re-read if uploaded_file is closed provided streamlit handles it? behavior varies.
    # Safe fallback: check session state for name or path if sample.
    
    source = None
    if "uploaded_file_obj" in st.session_state:
        source = st.session_state.uploaded_file_obj
    elif "selected_sample" in st.session_state:
        source = st.session_state.selected_sample
        
    exif_data = extract_exif(source) if source else {}

    if exif_data:
        # Check if it's a status message
        if "Status" in exif_data and len(exif_data) == 1:
            st.info(exif_data["Status"])
        else:
            # Format for dataframe
            formatted_data = [
                {"Tag": k, "Value": str(v)} for k, v in exif_data.items()
            ]
            df = pd.DataFrame(formatted_data)

            st.dataframe(
                df,
                column_config={
                    "Tag": st.column_config.TextColumn("Tag", width="medium"),
                    "Value": st.column_config.TextColumn("Value", width="large"),
                },
                use_container_width=True,
                hide_index=True,
            )
    else:
        st.info("No EXIF data found.")
