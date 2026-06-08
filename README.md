# Cryptocurrency Volatility Predictor
### Live 7-Day Volatility Forecasting | Random Forest + XGBoost | Deployed on AWS EC2

---

## What Business Problem Does This Solve?

Crypto traders and portfolio managers face one core risk every day:
**not knowing how volatile an asset will be in the next week.**

High volatility = high risk. If you can forecast it 7 days ahead, you can:
- Size your position correctly before entering a trade
- Decide when to hedge your portfolio
- Avoid entering a position the day before a volatility spike

**This project answers:**
> *"Based on today's price action, how volatile will this crypto be over the next 7 days?"*

---

## Business Results

| Metric | Value |
|---|---|
| Forecast horizon | 7-day forward annualised volatility |
| Data source | Real-time OHLCV via yfinance (live market data) |
| Cryptos supported | BTC, ETH, BNB, and more |
| Models | Random Forest + XGBoost ensemble |
| Deployment | Live on AWS EC2 — 3-container Docker architecture |

---

## Key Features

- **Live data** — pulls real-time price data at inference time via yfinance, no stale predictions
- **7-day forward forecast** — actionable trading horizon, not just historical analysis
- **Annualised volatility** — standard metric used by traders, risk managers, and quant analysts
- **Three interfaces** — Flask UI (main), FastAPI (REST endpoint with Swagger docs), Streamlit (analytics view)
- **Production monitoring** — Prometheus metrics tracking model performance and uptime

---

## Live Demo

🌐 **[Live App — Flask UI](http://43.205.113.174:5000)**
📡 **[REST API — FastAPI + Swagger](http://43.205.113.174:8000/docs)**

---

## How It Works

```
Real-Time OHLCV Data (yfinance)
    │  Open · High · Low · Close · Volume
    ▼
Feature Engineering
    │  Rolling returns · Historical volatility windows
    │  Price momentum · Volume signals
    ▼
ML Ensemble (Random Forest + XGBoost)
    │  Trained on historical crypto price data
    ▼
7-Day Forward Annualised Volatility Forecast
    └── Displayed on Flask UI + available via REST API
```

---

## Production Architecture (AWS EC2)

```
AWS EC2 t2.medium
└── docker-compose.yml
    ├── Flask container      → Port 5000  (Main UI)
    ├── FastAPI container    → Port 8000  (REST API)
    └── Streamlit container  → Port 8501  (Analytics view)

CI/CD: GitHub Actions → auto-deploy on every push
Monitoring: Prometheus metrics on all containers
```

This is a **3-service microservices deployment** on a single EC2 instance,
orchestrated with Docker Compose and automated via GitHub Actions CI/CD.

---

## ML Model Details

| Parameter | Detail |
|---|---|
| Target variable | 7-day forward annualised volatility |
| Features | OHLCV-derived technical indicators |
| Models | Random Forest + XGBoost (ensemble) |
| Data source | yfinance (Yahoo Finance) — live at inference |
| Prediction type | Regression (volatility %) |

---

## Tech Stack

| Layer | Tool |
|---|---|
| Data | yfinance (real-time OHLCV) |
| ML models | Python, Scikit-Learn, XGBoost |
| Backend API | FastAPI (Swagger UI included) |
| Frontend | Flask (Google Material Design UI) |
| Analytics view | Streamlit |
| Deployment | Docker, Docker Compose, AWS EC2 |
| CI/CD | GitHub Actions |
| Monitoring | Prometheus |

---

## How to Run Locally

```bash
# 1. Clone the repo
git clone https://github.com/premchavan772005-spec/-Cryptocurrency-Volatility-Predictor

# 2. Build and run all 3 containers
docker-compose up --build

# Flask UI    → http://localhost:5000
# FastAPI     → http://localhost:8000/docs
# Streamlit   → http://localhost:8501
```

---

*Built by Prem Chavan | Data Analyst*
*Skills: Python · Machine Learning · FastAPI · Docker · AWS EC2 · CI/CD · Real-Time Data*
