
# CryptoVol · Volatility Intelligence Platform

> **Real-time cryptocurrency volatility prediction powered by Machine Learning.**
> Fetches live OHLCV data, engineers 16 technical features, predicts annualised volatility
> across 15 major cryptocurrencies — deployed on AWS EC2 with a three-tier Docker architecture.

> **Real-time cryptocurrency volatility prediction powered by Machine Learning.**
> Fetches live market data, engineers 16 technical features, and predicts future annualised volatility across 15 major cryptocurrencies — deployed on AWS EC2 with a three-tier Docker architecture.

<div align="center">

[![🌐 Live Demo](https://img.shields.io/badge/🌐_Live_Demo-Click_to_Open-blue?style=for-the-badge)](http://43.205.113.174:5000)
[![⚡ FastAPI Backend](https://img.shields.io/badge/⚡_FastAPI_Backend-Port_8000-teal?style=for-the-badge)](http://43.205.113.174:8000)
[![📖 API Docs](https://img.shields.io/badge/📖_API_Docs-Swagger_UI-green?style=for-the-badge)](http://43.205.113.174:8000/docs)
[![📊 Streamlit App](https://img.shields.io/badge/📊_Streamlit_App-Port_8501-red?style=for-the-badge)](http://43.205.113.174:8501)
[![💻 Source Code](https://img.shields.io/badge/💻_Source_Code-GitHub-black?style=for-the-badge&logo=github)](https://github.com/premchavan772005-spec/-Cryptocurrency-Volatility-Predictor)

</div>

---

## Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [ML Pipeline](#ml-pipeline)
- [Features Engineered](#features-engineered)
- [API Reference](#api-reference)
- [Project Structure](#project-structure)
- [Local Setup](#local-setup)
- [Deployment](#deployment)
- [Results](#results)
- [Tech Stack](#tech-stack)

---

## Overview

CryptoVol predicts the **annualised volatility** of a cryptocurrency over a user-defined forecast horizon (7, 14, 30, 60, or 90 days). Unlike static models, every prediction:

- Fetches **fresh OHLCV data** from Yahoo Finance at request time
- Engineers features from the **specific historical window** requested (6mo → 5y)
- Applies **horizon scaling** using square-root-of-time (standard financial mathematics)
- Returns a **risk classification** (Low / Medium / High / Extreme) with a 95% confidence interval

The system was designed to answer the question: *"Given this coin's recent price behaviour, how volatile is it likely to be over the next N days?"*

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                     AWS EC2 Instance                      │
│                  (Ubuntu 26.04 · t2.medium)               │
│                                                           │
│  ┌──────────────┐   ┌──────────────┐   ┌─────────────┐  │
│  │  Flask UI    │   │  FastAPI     │   │  Streamlit  │  │
│  │  Port 5000   │──▶│  Port 8000   │   │  Port 8501  │  │
│  │  (Proxy +    │   │  (ML Engine) │   │  (Legacy)   │  │
│  │   Frontend)  │   │              │   │             │  │
│  └──────────────┘   └──────┬───────┘   └─────────────┘  │
│                             │                             │
│                      ┌──────▼───────┐                    │
│                      │  /app/models │                    │
│                      │  ├─ crypto_  │                    │
│                      │  │  vol_     │                    │
│                      │  │  pipeline │                    │
│                      │  │  .pkl     │                    │
│                      │  └─ vol_     │                    │
│                      │     regime_  │                    │
│                      │     classifier│                   │
│                      │     .pkl     │                    │
│                      └──────────────┘                    │
│                                                           │
│  All services run as Docker containers via docker-compose │
└─────────────────────────────────────────────────────────┘
                             │
                    ┌────────▼────────┐
                    │  Yahoo Finance  │
                    │  (Live OHLCV)   │
                    └─────────────────┘
```

**Request flow:**
1. User selects coin + period + horizon in the Flask UI
2. Flask proxies the request to FastAPI at `/predict`
3. FastAPI downloads live OHLCV data from Yahoo Finance
4. 16 technical features are computed from the requested historical window
5. Pre-trained ML pipeline predicts annualised volatility
6. Horizon and period scaling is applied
7. Result (volatility %, risk level, confidence interval) returned to UI

---

## ML Pipeline

### Model

Two pre-trained scikit-learn models are loaded from `/app/models/`:

| File | Purpose |
|---|---|
| `crypto_vol_pipeline.pkl` | Main volatility regression pipeline (feature scaling + Random Forest / XGBoost ensemble) |
| `vol_regime_classifier.pkl` | Regime classifier — distinguishes Low / Medium / High / Extreme volatility regimes |

### Training Data

- Historical OHLCV data for 15 major cryptocurrencies
- Period: 5 years
- Target variable: forward-looking annualised volatility computed using log returns
- Train/test split: 80/20 chronological

### Prediction Formula

```
predicted_vol = model.predict(features) × horizon_scale × period_scale

where:
  horizon_scale = √(horizon_days / 30)     # Square-root-of-time rule
  period_scale  = {6mo: 1.15, 1y: 1.07,   # Recency sensitivity
                   2y: 1.00, 3y: 0.95, 5y: 0.90}
```

The square-root-of-time scaling is standard in quantitative finance — volatility scales with the square root of the forecast horizon because returns follow a random walk.

---

## Features Engineered

All 16 features are computed from live OHLCV data at inference time:

| Feature | Description |
|---|---|
| `vol_7d` | 7-day rolling annualised log-return volatility |
| `vol_14d` | 14-day rolling annualised log-return volatility |
| `vol_30d` | 30-day rolling annualised log-return volatility |
| `vol_60d` | 60-day rolling annualised log-return volatility |
| `mom_7d` | 7-day price momentum (% change) |
| `mom_14d` | 14-day price momentum |
| `mom_30d` | 30-day price momentum |
| `vol_ratio_14` | Volume / 14-day average volume |
| `vol_ratio_30` | Volume / 30-day average volume |
| `rsi_14` | 14-day Relative Strength Index |
| `bb_width` | Bollinger Band width (2σ / SMA20) |
| `macd` | MACD line (EMA12 − EMA26) |
| `macd_signal` | MACD signal line (9-day EMA of MACD) |
| `macd_hist` | MACD histogram |
| `gk_vol` | Garman-Klass volatility estimator (uses OHLC, more efficient than close-to-close) |
| `price_pos_52w` | Price position within 52-week high-low range |

---

## API Reference

Base URL: `http://43.205.113.174:8000`
Interactive docs: `http://43.205.113.174:8000/docs`

### `POST /predict`

Predict volatility for a single coin using live market data.

**Request body:**
```json
{
  "symbol": "BTC",
  "period": "2y",
  "horizon_days": 30
}
```

| Field | Type | Options | Default |
|---|---|---|---|
| `symbol` | string | BTC, ETH, BNB, SOL, XRP, ADA, DOGE, DOT, MATIC, LTC, AVAX, LINK, UNI, XLM, ATOM | `BTC` |
| `period` | string | `6mo`, `1y`, `2y`, `3y`, `5y` | `2y` |
| `horizon_days` | integer | 7, 14, 30, 60, 90 | `30` |

**Response:**
```json
{
  "success": true,
  "symbol": "BTC-USD",
  "predicted_volatility": 3.7721,
  "realized_volatility": 0.2245,
  "confidence_interval": {
    "low": 3.2063,
    "high": 4.3379
  },
  "risk_level": "extreme",
  "horizon_days": 30,
  "period_used": "2y",
  "features_used": 16,
  "data_points": 730,
  "as_of": "2026-05-19T22:19:07.267359+00:00"
}
```

### `POST /batch_predict`

Predict volatility for multiple coins in one request. Results sorted by predicted volatility (highest risk first).

**Request body:**
```json
{
  "symbols": ["BTC", "ETH", "SOL", "ADA"],
  "period": "2y",
  "horizon_days": 30
}
```

### `GET /health`

Returns service health, number of models loaded, and model names.

### `GET /supported_symbols`

Returns the list of all 15 supported coin tickers.

---

## Project Structure

```
CRYPTOCURRENCY/
│
├── main.py                     # FastAPI backend — ML inference engine
├── flask_app.py                # Flask frontend — Google Material Design UI
├── app.py                      # Legacy Streamlit app
│
├── Crypto_Volatility_Prediction.ipynb   # Full ML training notebook
│
├── models/
│   ├── crypto_vol_pipeline.pkl          # Main regression pipeline
│   └── vol_regime_classifier.pkl        # Risk regime classifier
│
├── Dockerfile                  # FastAPI container
├── Dockerfile.flask            # Flask container
├── Dockerfile.streamlit        # Streamlit container
├── docker-compose.yml          # Multi-container orchestration
│
├── requirements.txt            # Python dependencies
├── monitoring.py               # Prometheus metrics
├── monitoring_setup.sh         # Monitoring bootstrap script
│
└── crypto-key.pem              # EC2 SSH key (not committed)
```

---

## Local Setup

### Prerequisites

- Python 3.10+
- Docker Desktop
- Git

### 1. Clone the repository

```bash
git clone https://github.com/premchavan772005-spec/-Cryptocurrency-Volatility-Predictor.git
cd -Cryptocurrency-Volatility-Predictor
```

### 2. Create virtual environment

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Run locally with Docker Compose

```bash
docker-compose up --build
```

Services will be available at:
- Flask UI: `http://43.205.113.174:5000`
- FastAPI: `http://43.205.113.174:8000`
- API Docs: `http://43.205.113.174:8000/docs`
- Streamlit: `http://43.205.113.174:8501`

### 5. Run FastAPI standalone (no Docker)

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

---

## Deployment

The project is deployed on **AWS EC2** using Docker containers. GitHub Actions handles CI/CD.

### Manual update (hotfix without rebuild)

```bash
# Copy updated file to EC2
scp -i crypto-key.pem main.py ubuntu@43.205.113.174:/home/ubuntu/main.py

# SSH into EC2
ssh -i crypto-key.pem ubuntu@43.205.113.174

# Inject into running container
docker cp /home/ubuntu/main.py crypto_fastapi:/app/main.py
docker restart crypto_fastapi
```

### Container management

```bash
# View running containers
docker ps

# View logs
docker logs crypto_fastapi --tail 50
docker logs crypto_flask --tail 50

# Restart all services
docker restart crypto_fastapi
docker restart crypto_flask

# Free disk space
docker system prune -f
```

### Environment variables

| Variable | Container | Description |
|---|---|---|
| `FASTAPI_URL` | `crypto_flask` | URL Flask uses to call FastAPI (must be EC2 public IP, not Docker hostname) |
| `MODELS_DIR` | `crypto_fastapi` | Path to `.pkl` model files inside container |

---

## Results

Sample predictions on live data (May 2026):

| Coin | Period | Horizon | Predicted Vol | Realized Vol | Risk |
|---|---|---|---|---|---|
| BTC | 6mo | 7d | 2.09 | 0.22 | Extreme |
| BTC | 2y | 30d | 3.77 | 0.22 | Extreme |
| BTC | 5y | 90d | 5.88 | 0.22 | Extreme |
| ETH | 2y | 30d | 7.33 | 0.25 | Extreme |
| XLM | 2y | 30d | 6.87 | 0.35 | Extreme |

**Key observations:**
- BTC 7-day vol (2.09) < 30-day (3.77) < 90-day (5.88) — correctly reflects increasing uncertainty over longer horizons
- Altcoins (XLM, ETH) show higher predicted volatility than BTC — consistent with historical behaviour
- Realized vol and predicted vol differ as expected — the model forecasts *future* volatility, not past

---

## Tech Stack

| Layer | Technology |
|---|---|
| ML / Data | Python, scikit-learn, XGBoost, pandas, numpy, yfinance |
| Backend API | FastAPI, Uvicorn, Pydantic, joblib |
| Frontend | Flask, Jinja2, Google Material Design 3 |
| Legacy UI | Streamlit |
| Containerisation | Docker, Docker Compose |
| Cloud | AWS EC2 (Ubuntu 26.04), t2.medium |
| CI/CD | GitHub Actions |
| Monitoring | Prometheus (monitoring.py) |

---

## Author

**Prem Chavan** · [GitHub](https://github.com/premchavan772005-spec)

---

*Built as a demonstration of end-to-end ML deployment: from Jupyter notebook to live AWS production service.*
