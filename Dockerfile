FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y \
    curl \
    libgl1 \
    libglib2.0-0 \
    libcairo2 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8501

HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health || exit 1

ENTRYPOINT ["sh", "-c", \
    "python3 -c \"import streamlit, os; \
    path = os.path.join(os.path.dirname(streamlit.__file__), 'static', 'index.html'); \
    content = open(path).read(); \
    url = os.environ.get('UMAMI_URL'); \
    uid = os.environ.get('UMAMI_ID'); \
    script = f'<script id=\\\"umami-script\\\" defer src=\\\"{url}\\\" data-website-id=\\\"{uid}\\\"></script>'; \
    open(path, 'w').write(content.replace('</head>', f'{script}</head>')) if url and uid and 'umami-script' not in content else None\" \
    && streamlit run app.py --server.port=8501 --server.address=0.0.0.0 --server.enableCORS=false"]
