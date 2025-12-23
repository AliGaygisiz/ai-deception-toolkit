# The AI Deception Toolkit 🎭

**A forensic sandbox for analyzing and manipulating AI-generated imagery.**

Designed as a companion to the blog post *"[How to Trick AI Detectors](https://alig.dev/blog/why-ai-detectors-unreliable/)"*.

## Features

1. ### **The Scanner**: Checks various aspects of the image to give you an idea of how detectable it is.
   - Check the 3D Topology of the image
   - Check the Frequency Map of the image
   - Check the Exif Data of the image
2. ### **Humanizer**: Modify an AI generated image to deceive the detectors into thinking it's a real image.
   - Crop the image in a different aspect ratio
   - Change the perspective of the image slightly
   - Flip the image
   - Add lens distortion
   - Add Bayer Sensor Softness
   - Add ISO Grain
   - Add camera info to EXIF data
   - Add GPS location to EXIF data
3. ### **Faker**: Modify a real image to deceive the detectors into thinking it's an AI generated image.
   - Crop the image in a different aspect ratio
   - Add spectral grid artifacts
   - Add smoothness that is common in AI images
   - Add unsharp mask to enhance edges
   - Add Chrominance blur
   - Add AI Model tag to EXIF data
   - Add prompt info to EXIF data

---

## Quick Start (Local)

### Prerequisites
*   Python 3.10+
*   pip

### Installation

1.  **Clone the repository**
    ```bash
    git clone https://github.com/yourusername/ai-deception-toolkit.git
    cd ai-deception-toolkit
    ```

2.  **Install Dependencies**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Run the App**
    ```bash
    streamlit run app.py
    ```
    The application will open in your browser at `http://localhost:8501`.

---

## 🔓 Unlocking Full Power (Remove Limits)

By default, this repository is configured for **low-resource deployment** (e.g., a $5/mo VPS with 512MB RAM). It enforces a **1024px** resolution limit to prevent crashes.

**If you are running this locally on a powerful machine, you should remove these limits.**

### 1. Increase Resolution
Open `core/utils.py` and modify the `convert_to_rgb` function:

```python
# core/utils.py

# CHANGE THIS VALUE
max_dim = 4096  # Increase from 1024 to 4096 (or higher)
```

### 2. Increase Upload Size (Optional)
Open `.streamlit/config.toml`:
```toml
[server]
maxUploadSize = 200 # Increase from 10 to 200 (MB)
```

### 3. Docker Limits (If using Docker)
If you are deploying with Docker Compose, open `docker-compose.yml` and adjust the resources:
```yaml
deploy:
  resources:
    limits:
      cpus: '4.0'   # Increase
      memory: 8G    # Increase
```

---

## Project Structure

```text
ai-deception-toolkit/
├── assets/             # Sample images (AI/Real)
├── core/               # Application Logic
│   ├── analyzer.py     # FFT & Spectral Analysis
│   ├── metadata.py     # EXIF/XMP/PNG Parser
│   ├── processor.py    # Image Manipulation Kernels
│   └── utils.py        # Helpers & CONFIGURATION (Limits)
├── app.py              # Main Streamlit Interface
├── Dockerfile          # Container Definition
└── requirements.txt    # Python Dependencies
```

## Privacy Note
This tool processes images **locally in RAM**. No images are uploaded to any external server or saved to disk (except for temporary memory buffers during your session).

---

**License**: MIT
