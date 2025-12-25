import streamlit as st
import numpy as np
import io
from PIL import Image
from core.utils import load_css
from core.navigation import make_sidebar
from core.processor import (
    apply_crop,
    artificial_plasticity_v4,
    apply_unsharp_mask,
    chroma_smoothing,
    spectral_grid_injection_v4,
    apply_gemini_watermark,
)
from core.metadata import process_metadata
from core.ui import render_comparison_row

st.set_page_config(
    page_title="The Faker - AI Deception Toolkit",
    page_icon="🎭",
    layout="wide"
)

make_sidebar()
load_css()

st.header("The Faker")

# State Check
if "original_array" not in st.session_state or st.session_state.original_array is None:
    st.warning("⚠️ No image loaded. Please upload an image on the Home page.")
    st.page_link("app.py", label="Go to Home", icon="🏠")
    st.stop()

original_array = st.session_state.original_array

col_img, col_tools = st.columns([1.5, 1])

with col_tools:
    with st.form("faker_form"):
        st.subheader("Configuration")

        with st.expander("📐 Composition", expanded=True):
            f_crop = st.selectbox(
                "Crop Aspect Ratio",
                [
                    "Original",
                    "1:1 (Square)",
                    "4:5 (Portrait)",
                    "16:9 (Landscape)",
                    "9:16 (Story)",
                ],
            )

        with st.expander("🧬 Generative Artifacts", expanded=True):
            f_grid = st.slider("Stealth Spectral Grid", 0.0, 1.0, 0.6)
            f_plastic = st.slider("Plasticity Smoothing", 0.0, 1.0, 0.5)
            f_crisp = st.slider(
                "AI Crispness (Unsharp)",
                0.0,
                1.0,
                0.4,
                help="Simulates hyper-real edge contrast.",
            )
            f_chroma = st.slider("Chrominance Blur", 0.0, 1.0, 0.4)

        with st.expander("🏷️ AI Signing"):
            f_profile = st.selectbox(
                "Model Signature",
                ["None", "Google Tag", "ChatGPT Tag", "Midjourney Tag"],
            )
            f_prompt = st.text_area("Prompt", "A futuristic cyberpunk city...")
            f_gemini = st.checkbox("Add Gemini Icon Watermark", value=True)

        run_btn = st.form_submit_button("Run Injection", type="primary")

if run_btn:
    with st.spinner("Injecting generative artifacts..."):
        current = original_array.copy()
        current = apply_crop(current, f_crop)
        current = artificial_plasticity_v4(current, f_plastic)
        current = apply_unsharp_mask(current, f_crisp)
        current = chroma_smoothing(current, f_chroma)
        current = spectral_grid_injection_v4(current, f_grid)
        current = apply_gemini_watermark(current, f_gemini)

        img_pil = Image.fromarray(current)
        buf = io.BytesIO()
        img_pil.save(buf, format="PNG")
        img_bytes = buf.getvalue()

        f_params = {"prompt": f_prompt}
        if f_profile != "None":
            img_bytes = process_metadata(img_bytes, f_profile, f_params)

        st.session_state.processed_image = img_bytes
        st.session_state.processing_type = f"faked"

with col_img:
    if st.session_state.get("processed_image") and "faked" in str(
        st.session_state.get("processing_type")
    ):
        st.subheader("Injection Result")
        res_img = Image.open(io.BytesIO(st.session_state.processed_image))
        res_arr = np.array(res_img)
        st.image(res_img, width="stretch")
        fname = st.session_state.get("input_filename", "image") + "_faked.png"
        st.download_button(
            "⬇️ Download Result",
            st.session_state.processed_image,
            fname,
            "image/png",
        )

    else:
        st.subheader("Original Preview")
        st.image(original_array, width="stretch", caption="Source")

# Full Width Analysis
if st.session_state.get("processed_image") and "faked" in str(
    st.session_state.get("processing_type")
):
    res_img_full = Image.open(io.BytesIO(st.session_state.processed_image))
    res_arr_full = np.array(res_img_full)
    render_comparison_row(original_array, res_arr_full)
