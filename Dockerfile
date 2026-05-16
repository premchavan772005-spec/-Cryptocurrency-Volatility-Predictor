# ============================================================
# Dockerfile — Cryptocurrency Volatility Predictor
# ============================================================
# Build:  docker build -t crypto-vol-predictor .
# Run:    docker run -p 8000:8000 crypto-vol-predictor
# ============================================================

# ── Base image ────────────────────────────────────────────────
FROM python:3.10.11-slim

# ── Set working directory ─────────────────────────────────────
WORKDIR /app

# ── Environment variables ─────────────────────────────────────
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    MODEL_DIR=/app/models

# ── Install system dependencies ───────────────────────────────
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# ── Copy requirements first (for Docker cache) ────────────────
COPY requirements.txt .

# ── Install Python dependencies ───────────────────────────────
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# ── Copy all project files ────────────────────────────────────
COPY . .

# ── Expose port ───────────────────────────────────────────────
EXPOSE 8000

# ── Run FastAPI with uvicorn ──────────────────────────────────
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
