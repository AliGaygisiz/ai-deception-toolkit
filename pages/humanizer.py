import streamlit as st
import numpy as np
import io
from PIL import Image
from core.utils import load_css
from core.navigation import make_sidebar
from core.processor import (
    apply_flip,
    apply_perspective_warp,
    apply_crop,
    apply_cfa_resampling,
    apply_chromatic_aberration,
    apply_iso_grain,
)
from core.metadata import process_metadata
from core.ui import render_comparison_row

st.set_page_config(
    page_title="The Humanizer - AI Deception Toolkit",
    page_icon="📷",
    layout="wide"
)

make_sidebar()
load_css()

st.header("The Humanizer")

# State Check
if "original_array" not in st.session_state or st.session_state.original_array is None:
    st.warning("⚠️ No image loaded. Please upload an image on the Home page.")
    st.page_link("app.py", label="Go to Home", icon="🏠")
    st.stop()

original_array = st.session_state.original_array

col_img, col_tools = st.columns([1.5, 1])

with col_tools:
    with st.form("humanizer_form"):
        st.subheader("Configuration")

        with st.expander("📐 Composition & Geometry", expanded=True):
            h_crop = st.selectbox(
                "Crop Aspect Ratio",
                [
                    "Original",
                    "1:1 (Square)",
                    "4:5 (Portrait)",
                    "16:9 (Landscape)",
                    "9:16 (Story)",
                ],
            )
            h_perp = st.slider(
                "Perspective Adjustment",
                0.0,
                1.0,
                0.0,
                help="Simulate random camera tilt/angle.",
            )
            h_flip = st.checkbox(
                "Mirror Image (Flip)", help="Simulate selfie mode."
            )

        with st.expander("🎞️ Optical Physics", expanded=True):
            h_optics = st.slider("Lens Distortion", 0.0, 1.0, 0.1)  # User default
            h_cfa = st.checkbox(
                "Bayer Sensor Softness", value=False
            )  # User default
            h_grain = st.slider(
                "ISO Grain (Shot Noise)", 0.0, 1.0, 0.1
            )  # User default

        with st.expander("📝 Metadata Injection"):
            h_profile = st.selectbox(
                "Camera Model", ["None", "iPhone 15 Pro", "Sony A7III"]
            )
            enable_gps = st.checkbox("Inject GPS")
            lat = st.number_input("Latitude", 40.7128)
            lon = st.number_input("Longitude", -74.0060)

        run_btn = st.form_submit_button("Run Simulation", type="primary")

if run_btn:
    with st.spinner("Simulating optical path..."):
        current = original_array.copy()
        # Pipeline: Flip -> Crop -> Perspective -> CFA -> Optics -> Noise
        current = apply_flip(current, h_flip)
        current = apply_crop(current, h_crop)
        current = apply_perspective_warp(current, h_perp)
        current = apply_cfa_resampling(current, h_cfa)
        current = apply_chromatic_aberration(current, h_optics)
        current = apply_iso_grain(current, h_grain)

        img_pil = Image.fromarray(current)
        buf = io.BytesIO()
        img_pil.save(buf, format="JPEG", quality=95)
        img_bytes = buf.getvalue()

        if h_profile != "None":
            params = {"lat": lat, "lon": lon} if enable_gps else {}
            img_bytes = process_metadata(img_bytes, h_profile, params)

        st.session_state.processed_image = img_bytes
        st.session_state.processing_type = f"humanized"

with col_img:
    if st.session_state.get("processed_image") and "humanized" in str(
        st.session_state.get("processing_type")
    ):
        st.subheader("Simulation Result")
        res_img = Image.open(io.BytesIO(st.session_state.processed_image))
        res_arr = np.array(res_img)
        st.image(res_img, width="stretch")
        fname = st.session_state.get("input_filename", "image") + "_humanized.jpg"
        st.download_button(
            "⬇️ Download Result",
            st.session_state.processed_image,
            fname,
            "image/jpeg",
        )

    else:
        st.subheader("Original Preview")
        st.image(original_array, width="stretch", caption="Source")

# Full Width Analysis
if st.session_state.get("processed_image") and "humanized" in str(
    st.session_state.get("processing_type")
):
    # Re-load array for analysis (or check if it persists, safe to reload from bytes)
    res_img_full = Image.open(io.BytesIO(st.session_state.processed_image))
    res_arr_full = np.array(res_img_full)
    render_comparison_row(original_array, res_arr_full)
