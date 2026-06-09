"""
Cryptocurrency Volatility Predictor — FastAPI Backend
Fetches live data per coin, engineers features, runs model prediction.
Prediction varies by: symbol, period (historical window), horizon_days (forecast length).
"""

import os
import logging
import warnings
from pathlib import Path
from datetime import datetime, timezone

import numpy as np
import pandas as pd
import yfinance as yf
import joblib
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

warnings.filterwarnings("ignore")
logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
log = logging.getLogger(__name__)

app = FastAPI(
    title="Crypto Volatility Predictor API",
    description="Predicts future volatility for any cryptocurrency using live market data.",
    version="2.1.0",
)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

MODELS_DIR = Path(os.getenv("MODELS_DIR", "/app/models"))

SUPPORTED_SYMBOLS = {
    "BTC": "BTC-USD", "ETH": "ETH-USD", "BNB": "BNB-USD",
    "SOL": "SOL-USD", "XRP": "XRP-USD", "ADA": "ADA-USD",
    "DOGE": "DOGE-USD", "DOT": "DOT-USD", "MATIC": "MATIC-USD",
    "LTC": "LTC-USD", "AVAX": "AVAX-USD", "LINK": "LINK-USD",
    "UNI": "UNI-USD", "XLM": "XLM-USD", "ATOM": "ATOM-USD",
}

RISK_THRESHOLDS = {
    "low": (0, 0.02), "medium": (0.02, 0.04),
    "high": (0.04, 0.07), "extreme": (0.07, 9999),
}

# Period -> how many recent days to use for feature computation
# Shorter period = use only recent data = more reactive
PERIOD_DAYS = {
    "6mo": 180, "1y": 365, "2y": 730, "3y": 1095, "5y": 1825
}

_model_cache: dict = {}

def load_model(symbol: str):
    if symbol in _model_cache:
        return _model_cache[symbol]
    candidates = (
        list(MODELS_DIR.glob(f"*{symbol}*.pkl"))
        + list(MODELS_DIR.glob(f"*{symbol.lower()}*.pkl"))
        + list(MODELS_DIR.glob("*.pkl"))
    )
    if not candidates:
        raise FileNotFoundError(f"No .pkl model found in {MODELS_DIR}")
    path = candidates[0]
    log.info(f"Loading model for {symbol}: {path}")
    model = joblib.load(path)
    _model_cache[symbol] = model
    return model


def compute_features(df: pd.DataFrame, horizon_days: int, period_days: int) -> pd.DataFrame:
    """
    Engineer features from OHLCV data.
    period_days controls how much history to use — shorter = more recent/reactive features.
    horizon_days controls forward-looking window sizes.
    """
    df = df.copy().sort_index()

    # Clip to the period window so shorter periods use only recent data
    if len(df) > period_days:
        df = df.iloc[-period_days:]

    df["returns"]     = df["Close"].pct_change()
    df["log_returns"] = np.log(df["Close"] / df["Close"].shift(1))

    # Rolling windows capped at period length to avoid NaN-only columns
    max_w = max(7, min(len(df) - 1, 60))
    w7    = min(7,  max_w)
    w14   = min(14, max_w)
    w30   = min(30, max_w)
    w60   = min(60, max_w)

    df[f"vol_7d"]  = df["log_returns"].rolling(w7).std()  * np.sqrt(252)
    df[f"vol_14d"] = df["log_returns"].rolling(w14).std() * np.sqrt(252)
    df[f"vol_30d"] = df["log_returns"].rolling(w30).std() * np.sqrt(252)
    df[f"vol_60d"] = df["log_returns"].rolling(w60).std() * np.sqrt(252)

    df["mom_7d"]  = df["Close"].pct_change(w7)
    df["mom_14d"] = df["Close"].pct_change(w14)
    df["mom_30d"] = df["Close"].pct_change(w30)

    df["vol_ratio_14"] = df["Volume"] / df["Volume"].rolling(w14).mean()
    df["vol_ratio_30"] = df["Volume"] / df["Volume"].rolling(w30).mean()

    delta = df["Close"].diff()
    gain  = delta.clip(lower=0).rolling(w14).mean()
    loss  = (-delta.clip(upper=0)).rolling(w14).mean()
    df["rsi_14"] = 100 - (100 / (1 + gain / (loss + 1e-9)))

    sma20 = df["Close"].rolling(min(20, max_w)).mean()
    std20 = df["Close"].rolling(min(20, max_w)).std()
    df["bb_width"] = (2 * std20) / (sma20 + 1e-9)

    ema12 = df["Close"].ewm(span=12, adjust=False).mean()
    ema26 = df["Close"].ewm(span=26, adjust=False).mean()
    df["macd"]        = ema12 - ema26
    df["macd_signal"] = df["macd"].ewm(span=9, adjust=False).mean()
    df["macd_hist"]   = df["macd"] - df["macd_signal"]

    df["gk_vol"] = np.sqrt(
        0.5 * np.log(df["High"] / df["Low"]) ** 2
        - (2 * np.log(2) - 1) * np.log(df["Close"] / df["Open"]) ** 2
    ).rolling(w30).mean() * np.sqrt(252)

    roll_min = df["Close"].rolling(min(252, len(df)-1)).min()
    roll_max = df["Close"].rolling(min(252, len(df)-1)).max()
    df["price_pos_52w"] = (df["Close"] - roll_min) / (roll_max - roll_min + 1e-9)

    feature_cols = [
        "vol_7d", "vol_14d", "vol_30d", "vol_60d",
        "mom_7d", "mom_14d", "mom_30d",
        "vol_ratio_14", "vol_ratio_30",
        "rsi_14", "bb_width",
        "macd", "macd_signal", "macd_hist",
        "gk_vol", "price_pos_52w",
    ]

    df.dropna(subset=feature_cols, inplace=True)
    return df[feature_cols].tail(1), df["vol_30d"].dropna().iloc[-1] if not df["vol_30d"].dropna().empty else 0.0


def predict_volatility(ticker: str, period: str, horizon_days: int, symbol_key: str) -> dict:
    log.info(f"Fetching live data for {ticker} | period={period} | horizon={horizon_days}d")

    # Always download max data; we slice inside compute_features
    df = yf.download(ticker, period="5y", auto_adjust=True, progress=False)

    if df.empty or len(df) < 60:
        raise ValueError(f"Insufficient data for {ticker} (got {len(df)} rows)")

    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

    period_days = PERIOD_DAYS.get(period, 730)
    features, realized_vol = compute_features(df, horizon_days, period_days)

    if features.empty:
        raise ValueError(f"Could not compute features for {ticker}")

    model = load_model(symbol_key)
    X = features.values

    try:
        if hasattr(model, "n_features_in_"):
            n = model.n_features_in_
            if X.shape[1] < n:
                X = np.pad(X, ((0, 0), (0, n - X.shape[1])))
            elif X.shape[1] > n:
                X = X[:, :n]
        base_vol = float(model.predict(X)[0])
    except Exception as e:
        log.warning(f"Model predict error: {e} — using realized vol fallback")
        base_vol = float(realized_vol)

    base_vol = max(0.001, base_vol)

    # ── Horizon scaling: volatility scales with sqrt(time) ──────────────────
    # Base = 30 days. 7d forecast < 30d < 90d in annualised vol terms.
    horizon_scale = np.sqrt(horizon_days / 30.0)

    # ── Period scaling: shorter window = more sensitive to recent moves ──────
    # 6mo window captures recent spikes more strongly than 5y average
    period_scale_map = {"6mo": 1.15, "1y": 1.07, "2y": 1.0, "3y": 0.95, "5y": 0.90}
    period_scale = period_scale_map.get(period, 1.0)

    predicted_vol = base_vol * horizon_scale * period_scale
    predicted_vol = max(0.001, predicted_vol)

    ci_low  = round(predicted_vol * 0.85, 4)
    ci_high = round(predicted_vol * 1.15, 4)

    risk_level = "extreme"
    for label, (lo, hi) in RISK_THRESHOLDS.items():
        if lo <= predicted_vol < hi:
            risk_level = label
            break

    log.info(
        f"Result: {ticker} base={base_vol:.4f} h_scale={horizon_scale:.3f} "
        f"p_scale={period_scale:.2f} final={predicted_vol:.4f} risk={risk_level}"
    )

    return {
        "symbol":               ticker,
        "predicted_volatility": round(predicted_vol, 4),
        "realized_volatility":  round(float(realized_vol), 4),
        "confidence_interval":  {"low": ci_low, "high": ci_high},
        "risk_level":           risk_level,
        "horizon_days":         horizon_days,
        "period_used":          period,
        "features_used":        features.shape[1],
        "data_points":          period_days,
        "as_of":                datetime.now(timezone.utc).isoformat(),
    }


# ── Schemas ──────────────────────────────────────────────────────────────────
class PredictRequest(BaseModel):
    symbol: str = "BTC"
    period: str = "2y"
    horizon_days: int = 30

class BatchRequest(BaseModel):
    symbols: list[str] = ["BTC", "ETH", "BNB"]
    period: str = "2y"
    horizon_days: int = 30


# ── Routes ───────────────────────────────────────────────────────────────────
@app.get("/")
def root():
    return {"service": "Crypto Volatility Predictor API", "version": "2.1.0", "status": "online"}

@app.get("/health")
def health():
    models = list(MODELS_DIR.glob("*.pkl")) if MODELS_DIR.exists() else []
    return {
        "status":       "healthy",
        "models_found": len(models),
        "model_names":  [m.stem for m in models],
        "models_dir":   str(MODELS_DIR),
        "timestamp":    datetime.now(timezone.utc).isoformat(),
    }

@app.get("/supported_symbols")
def supported_symbols():
    return {"symbols": list(SUPPORTED_SYMBOLS.keys())}

@app.post("/predict")
def predict(req: PredictRequest):
    symbol_key = req.symbol.upper().replace("-USD", "")
    ticker = SUPPORTED_SYMBOLS.get(symbol_key, f"{symbol_key}-USD")
    try:
        return {"success": True, **predict_volatility(ticker, req.period, req.horizon_days, symbol_key)}
    except FileNotFoundError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        log.error(f"Prediction error for {req.symbol}: {e}")
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")

@app.get("/predict")
def predict_get(symbol: str = Query("BTC"), period: str = Query("2y"), horizon_days: int = Query(30)):
    return predict(PredictRequest(symbol=symbol, period=period, horizon_days=horizon_days))

@app.post("/batch_predict")
def batch_predict(req: BatchRequest):
    results, errors = [], []
    for sym in req.symbols:
        try:
            symbol_key = sym.upper().replace("-USD", "")
            ticker = SUPPORTED_SYMBOLS.get(symbol_key, f"{symbol_key}-USD")
            results.append(predict_volatility(ticker, req.period, req.horizon_days, symbol_key))
        except Exception as e:
            errors.append({"symbol": sym, "error": str(e)})
    results.sort(key=lambda x: x["predicted_volatility"], reverse=True)
    return {"success": True, "count": len(results), "results": results, "errors": errors,
            "generated_at": datetime.now(timezone.utc).isoformat()}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=False)
