import streamlit as st
from core.analyzer import compute_fft, plot_2d_spectrum, plot_3d_spectrum
import random

def render_comparison_row(original_array, modified_array):
    """Renders side-by-side spectral analysis."""
    st.divider()
    with st.expander("📉 Spectral Analysis (Comparison)", expanded=True):
        c1, c2 = st.columns(2)

        # Compute FFTs
        mag_orig, _ = compute_fft(original_array)
        mag_mod, _ = compute_fft(modified_array)

        with c1:
            st.markdown("#### 🔹 Original Signal")
            st.pyplot(plot_2d_spectrum(mag_orig))
            st.plotly_chart(
                plot_3d_spectrum(mag_orig),
                key=f"3d_orig_{random.randint(0, 1000)}",
            )

        with c2:
            st.markdown("#### 🔸 Modified Signal")
            st.pyplot(plot_2d_spectrum(mag_mod))
            st.plotly_chart(
                plot_3d_spectrum(mag_mod),
                key=f"3d_mod_{random.randint(0, 1000)}",
            )
