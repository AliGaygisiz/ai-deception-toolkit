import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import plotly.graph_objects as go

@st.cache_data
def compute_fft(image_array):
    """Computes Magnitude Spectrum (Green Channel)."""
    g_channel = image_array[:, :, 1]
    f = np.fft.fft2(g_channel)
    fshift = np.fft.fftshift(f)
    result = 20 * np.log(np.abs(fshift) + 1e-9)
    return result, fshift

@st.cache_data
def plot_2d_spectrum(magnitude_spectrum):
    """Renders 2D frequency map using Matplotlib."""
    fig, ax = plt.subplots(figsize=(6, 6))
    with plt.style.context("dark_background"):
        ax.imshow(magnitude_spectrum, cmap='inferno')
        ax.set_title('Frequency Domain Analysis', fontsize=8, color='gray')
        ax.axis('off')
        fig.patch.set_facecolor('#0e1117')
    return fig

@st.cache_data
def plot_3d_spectrum(magnitude_spectrum, resolution=128):
    """Renders 3D topological surface map using Plotly."""
    h, w = magnitude_spectrum.shape
    scale_h = max(1, h // resolution)
    scale_w = max(1, w // resolution)
    downsampled = magnitude_spectrum[::scale_h, ::scale_w]
    
    fig = go.Figure(data=[go.Surface(
        z=downsampled, 
        colorscale='Viridis',
        contours_z=dict(show=True, usecolormap=True, highlightcolor="limegreen", project_z=True)
    )])
    
    fig.update_layout(
        title=dict(text='3D Signal Topology', x=0),
        autosize=True,
        width=800,
        height=600,
        margin=dict(l=20, r=20, b=20, t=50),
        scene=dict(
            xaxis=dict(showgrid=False, backgroundcolor="rgba(0,0,0,0)"),
            yaxis=dict(showgrid=False, backgroundcolor="rgba(0,0,0,0)"),
            zaxis=dict(showgrid=True, title="Magnitude (dB)"),
            camera=dict(eye=dict(x=1.5, y=1.5, z=0.8))
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, sans-serif", color="white")
    )
    return fig
