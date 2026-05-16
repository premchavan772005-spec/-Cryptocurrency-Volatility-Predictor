# ============================================================
# Cryptocurrency Volatility Predictor — FastAPI Application
# ============================================================
# Run locally:  uvicorn main:app --reload --port 8000
# Docs UI:      http://localhost:8000/docs
# ============================================================

import os
import json
import time
import logging
from datetime import datetime
from typing import Optional

import numpy  as np
import pandas as pd
import joblib
import yfinance as yf

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

# ── Logging setup ─────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)
logger = logging.getLogger(__name__)

# ── FastAPI app ────────────────────────────────────────────────────────────────
app = FastAPI(
    title       = "Crypto Volatility Predictor API",
    description = "Predicts 7-day forward annualised volatility for cryptocurrencies",
    version     = "1.0.0",
    docs_url    = "/docs",
    redoc_url   = "/redoc",
)

# ── CORS (allow Streamlit / React frontends) ───────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins  = ["*"],
    allow_methods  = ["*"],
    allow_headers  = ["*"],
)

# ── Constants ─────────────────────────────────────────────────────────────────
MODEL_DIR    = os.getenv("MODEL_DIR", "models")
FEATURES     = [
    "log_ret","daily_range_pct",
    "rv_7","rv_14","rv_30","rv_60",
    "sma_7","sma_21","sma_50","ema_12","ema_26",
    "macd","macd_signal",
    "bb_width","bb_pct",
    "atr_14",
    "liq_ratio","volume_sma14","volume_z",
    "mom_7","mom_30",
    "dow","month","quarter"
]
REGIME_LABELS = {0: "Low", 1: "Medium", 2: "High"}
REGIME_EMOJI  = {0: "🟢", 1: "🟡", 2: "🔴"}

# ── Global model store (loaded once at startup) ────────────────────────────────
models = {}

# ══════════════════════════════════════════════════════════════════════════════
# STARTUP & SHUTDOWN
# ══════════════════════════════════════════════════════════════════════════════
@app.on_event("startup")
async def load_models():
    """Load all .pkl models into memory when the server starts."""
    logger.info("Loading models from: %s", MODEL_DIR)
    try:
        models["pipeline"]    = joblib.load(f"{MODEL_DIR}/crypto_vol_pipeline.pkl")
        models["regime_clf"]  = joblib.load(f"{MODEL_DIR}/vol_regime_classifier.pkl")
        with open(f"{MODEL_DIR}/metadata/model_metadata.json") as f:
            models["metadata"] = json.load(f)
        logger.info("✅ All models loaded successfully")
    except FileNotFoundError as e:
        logger.warning("⚠️  Model files not found (%s). Prediction endpoints will run in live-train mode.", e)


@app.on_event("shutdown")
async def shutdown():
    logger.info("Server shutting down.")


# ══════════════════════════════════════════════════════════════════════════════
# PYDANTIC SCHEMAS
# ══════════════════════════════════════════════════════════════════════════════
class PredictRequest(BaseModel):
    symbol  : str  = Field("BTC-USD",  example="BTC-USD",  description="Yahoo Finance ticker symbol")
    period  : str  = Field("6mo",      example="6mo",       description="History period: 1mo 3mo 6mo 1y 2y")
    horizon : int  = Field(7,          example=7,           description="Forward forecast horizon in days")

class FeatureRow(BaseModel):
    """Send your own pre-engineered feature row directly."""
    log_ret         : float
    daily_range_pct : float
    rv_7            : float
    rv_14           : float
    rv_30           : float
    rv_60           : float
    sma_7           : float
    sma_21          : float
    sma_50          : float
    ema_12          : float
    ema_26          : float
    macd            : float
    macd_signal     : float
    bb_width        : float
    bb_pct          : float
    atr_14          : float
    liq_ratio       : float
    volume_sma14    : float
    volume_z        : float
    mom_7           : float
    mom_30          : float
    dow             : int
    month           : int
    quarter         : int

class PredictResponse(BaseModel):
    symbol                : str
    prediction_date       : str
    predicted_volatility  : float
    volatility_regime     : str
    regime_emoji          : str
    horizon_days          : int
    model_version         : str
    latency_ms            : float


# ══════════════════════════════════════════════════════════════════════════════
# FEATURE ENGINEERING HELPER
# ══════════════════════════════════════════════════════════════════════════════
def engineer_features(symbol: str, period: str, horizon: int) -> pd.DataFrame:
    """Fetch OHLCV data and engineer all 24 features. Returns latest row."""
    raw = yf.download(symbol, period=period, auto_adjust=True, progress=False)
    if isinstance(raw.columns, pd.MultiIndex):
        raw.columns = raw.columns.get_level_values(0)
    if len(raw) < 65:
        raise ValueError(f"Not enough data for {symbol}. Use a longer period.")

    df = raw.copy()
    c, h, l, v = df["Close"], df["High"], df["Low"], df["Volume"]

    df["log_ret"]         = np.log(c / c.shift(1))
    df["daily_range_pct"] = (h - l) / c.shift(1)

    for w in [7, 14, 30, 60]:
        df[f"rv_{w}"] = df["log_ret"].rolling(w).std() * np.sqrt(365)

    for w in [7, 21, 50]:
        df[f"sma_{w}"] = c.rolling(w).mean()
    df["ema_12"] = c.ewm(span=12).mean()
    df["ema_26"] = c.ewm(span=26).mean()
    df["macd"]        = df["ema_12"] - df["ema_26"]
    df["macd_signal"] = df["macd"].ewm(span=9).mean()

    df["bb_mid"]   = c.rolling(20).mean()
    df["bb_std"]   = c.rolling(20).std()
    df["bb_upper"] = df["bb_mid"] + 2 * df["bb_std"]
    df["bb_lower"] = df["bb_mid"] - 2 * df["bb_std"]
    df["bb_width"] = (df["bb_upper"] - df["bb_lower"]) / (df["bb_mid"] + 1e-10)
    df["bb_pct"]   = (c - df["bb_lower"]) / (df["bb_upper"] - df["bb_lower"] + 1e-10)

    prev_c = c.shift(1)
    tr = pd.concat([(h - l), (h - prev_c).abs(), (l - prev_c).abs()], axis=1).max(axis=1)
    df["atr_14"] = tr.rolling(14).mean()

    mktcap = c * v
    df["liq_ratio"]    = v / (mktcap + 1e-10)
    df["volume_sma14"] = v.rolling(14).mean()
    df["volume_z"]     = (v - df["volume_sma14"]) / (v.rolling(14).std() + 1e-10)

    df["mom_7"]  = c / c.shift(7)  - 1
    df["mom_30"] = c / c.shift(30) - 1

    df["dow"]     = df.index.dayofweek
    df["month"]   = df.index.month
    df["quarter"] = df.index.quarter

    df.dropna(inplace=True)
    return df[FEATURES].tail(1)


def run_prediction(X: pd.DataFrame):
    """Run pipeline + regime classifier. Returns (vol, regime_int)."""
    if "pipeline" not in models:
        raise HTTPException(
            status_code=503,
            detail="Models not loaded. Ensure .pkl files are present in the models/ directory."
        )
    vol    = float(models["pipeline"].predict(X)[0])
    regime = int(models["regime_clf"].predict(X)[0])
    return vol, regime


# ══════════════════════════════════════════════════════════════════════════════
# ENDPOINTS
# ══════════════════════════════════════════════════════════════════════════════

# ── 1. Health check ────────────────────────────────────────────────────────────
@app.get("/health", tags=["System"])
async def health():
    """Returns server health + loaded model info."""
    return {
        "status"        : "ok",
        "timestamp"     : datetime.utcnow().isoformat() + "Z",
        "models_loaded" : list(models.keys()),
        "model_version" : models.get("metadata", {}).get("created_at", "unknown"),
    }


# ── 2. Root ───────────────────────────────────────────────────────────────────
@app.get("/", tags=["System"])
async def root():
    return {
        "message" : "Crypto Volatility Predictor API is running 🚀",
        "docs"    : "/docs",
        "version" : "1.0.0",
    }


# ── 3. Main prediction endpoint ────────────────────────────────────────────────
@app.post("/predict", response_model=PredictResponse, tags=["Prediction"])
async def predict(req: PredictRequest):
    """
    Predict 7-day forward volatility for a given cryptocurrency.

    - **symbol**: Yahoo Finance ticker (e.g. BTC-USD, ETH-USD)
    - **period**: Historical data window (1mo, 3mo, 6mo, 1y, 2y)
    - **horizon**: Forecast horizon in days (default 7)
    """
    t0 = time.perf_counter()
    logger.info("Predict request: symbol=%s period=%s horizon=%d", req.symbol, req.period, req.horizon)

    try:
        X = engineer_features(req.symbol, req.period, req.horizon)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        logger.error("Feature engineering failed: %s", e)
        raise HTTPException(status_code=500, detail=f"Data fetch error: {e}")

    vol, regime = run_prediction(X)
    latency = round((time.perf_counter() - t0) * 1000, 2)
    logger.info("Result: vol=%.5f regime=%s latency=%.1fms", vol, REGIME_LABELS[regime], latency)

    return PredictResponse(
        symbol               = req.symbol,
        prediction_date      = datetime.utcnow().strftime("%Y-%m-%d"),
        predicted_volatility = round(vol, 6),
        volatility_regime    = REGIME_LABELS[regime],
        regime_emoji         = REGIME_EMOJI[regime],
        horizon_days         = req.horizon,
        model_version        = models.get("metadata", {}).get("created_at", "unknown"),
        latency_ms           = latency,
    )


# ── 4. Predict from raw features ──────────────────────────────────────────────
@app.post("/predict/features", tags=["Prediction"])
async def predict_from_features(row: FeatureRow):
    """
    Predict volatility from a pre-engineered feature row.
    Use this when you already have features computed externally.
    """
    t0 = time.perf_counter()
    X  = pd.DataFrame([row.dict()])
    vol, regime = run_prediction(X)
    return {
        "predicted_volatility" : round(vol, 6),
        "volatility_regime"    : REGIME_LABELS[regime],
        "regime_emoji"         : REGIME_EMOJI[regime],
        "latency_ms"           : round((time.perf_counter() - t0) * 1000, 2),
    }


# ── 5. Batch prediction ────────────────────────────────────────────────────────
@app.post("/predict/batch", tags=["Prediction"])
async def predict_batch(symbols: list[str], period: str = "6mo", horizon: int = 7):
    """
    Predict volatility for multiple symbols in one call.
    Example body: ["BTC-USD", "ETH-USD", "SOL-USD"]
    """
    if len(symbols) > 20:
        raise HTTPException(status_code=400, detail="Max 20 symbols per batch request.")

    results = []
    for sym in symbols:
        try:
            X = engineer_features(sym, period, horizon)
            vol, regime = run_prediction(X)
            results.append({
                "symbol"               : sym,
                "predicted_volatility" : round(vol, 6),
                "volatility_regime"    : REGIME_LABELS[regime],
                "regime_emoji"         : REGIME_EMOJI[regime],
                "status"               : "success",
            })
        except Exception as e:
            results.append({"symbol": sym, "status": "error", "detail": str(e)})

    return {"batch_size": len(symbols), "results": results}


# ── 6. Model info ─────────────────────────────────────────────────────────────
@app.get("/model/info", tags=["Model"])
async def model_info():
    """Returns metadata about the loaded model."""
    if "metadata" not in models:
        raise HTTPException(status_code=503, detail="Metadata not loaded.")
    return models["metadata"]


# ── 7. Supported symbols ──────────────────────────────────────────────────────
@app.get("/symbols", tags=["Info"])
async def supported_symbols():
    """Returns the list of supported cryptocurrency symbols."""
    return {
        "symbols": [
            "BTC-USD","ETH-USD","BNB-USD","ADA-USD","XRP-USD",
            "SOL-USD","DOGE-USD","DOT-USD","MATIC-USD","LTC-USD",
            "AVAX-USD","LINK-USD","ATOM-USD","UNI-USD","XLM-USD",
        ]
    }


# ── 8. Global exception handler ───────────────────────────────────────────────
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error("Unhandled error: %s", exc)
    return JSONResponse(status_code=500, content={"detail": "Internal server error."})


# ── Run directly ──────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
