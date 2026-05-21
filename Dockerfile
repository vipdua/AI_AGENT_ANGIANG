FROM python:3.11

# ===================================================
# ⚙️ ENVIRONMENT
# ===================================================
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# HuggingFace cache
ENV HF_HOME=/app/hf_cache
ENV TRANSFORMERS_CACHE=/app/hf_cache

# Python path
ENV PYTHONPATH=/app

# Disable HF telemetry/log spam
ENV HF_HUB_DISABLE_TELEMETRY=1

# ===================================================
# 📂 WORKDIR
# ===================================================
WORKDIR /app

# ===================================================
# 📦 COPY REQUIREMENTS
# ===================================================
COPY requirements.txt .

# ===================================================
# 📦 INSTALL DEPENDENCIES
# ===================================================
RUN pip install --upgrade pip

RUN pip install \
    --no-cache-dir \
    --extra-index-url https://download.pytorch.org/whl/cpu \
    -r requirements.txt

# ===================================================
# 🤖 PRELOAD MODELS
# ===================================================

# Reranker model
RUN python -c "from sentence_transformers import CrossEncoder; CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2'); print('✅ Reranker cached.')"

# Embedding model
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2'); print('✅ Embedding cached.')"

# ===================================================
# 📦 COPY SOURCE CODE
# ===================================================
COPY . .

# ===================================================
# 🌐 EXPOSE PORTS
# ===================================================
EXPOSE 8000
EXPOSE 8501

# ===================================================
# 🚀 START SERVICES
# ===================================================
CMD ["sh", "-c", "\
    uvicorn api.main:app --host 0.0.0.0 --port 8000 & \
    streamlit run app.py --server.port 8501 --server.address 0.0.0.0 \
    "]