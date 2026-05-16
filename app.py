import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import warnings
warnings.filterwarnings("ignore")
 
# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Crypto Volatility Predictor",
    page_icon="📈",
    layout="wide"
)
 
# ── Title ─────────────────────────────────────────────────────────────────────
st.title("📈 Cryptocurrency Volatility Predictor")
st.markdown("Predicts **7-day forward annualised volatility** using historical OHLCV data and ML.")
st.markdown("---")
 
# ── Sidebar ───────────────────────────────────────────────────────────────────
st.sidebar.header("⚙️ Configuration")
 
SYMBOL = st.sidebar.selectbox(
    "Select Cryptocurrency",
    ["BTC-USD", "ETH-USD", "BNB-USD", "ADA-USD", "SOL-USD",
     "XRP-USD", "DOGE-USD", "MATIC-USD", "DOT-USD", "LTC-USD"],
    index=0
)
 
PERIOD = st.sidebar.selectbox(
    "Historical Data Period",
    ["1y", "2y", "3y", "5y"],
    index=2
)
 
N_ESTIMATORS = st.sidebar.slider("Random Forest Trees", 50, 300, 150, 50)
FORECAST_DAYS = st.sidebar.slider("Forecast Horizon (days)", 3, 30, 7)
 
st.sidebar.markdown("---")
run_btn = st.sidebar.button("🚀 Run Prediction", use_container_width=True)
 
# ── Feature Engineering ───────────────────────────────────────────────────────
def add_features(df: pd.DataFrame, horizon: int = 7) -> pd.DataFrame:
    df = df.copy().sort_index()
    c, h, l, v = df["Close"], df["High"], df["Low"], df["Volume"]
 
    df["log_ret"]         = np.log(c / c.shift(1))
    df["daily_range_pct"] = (h - l) / c.shift(1)
 
    for w in [7, 14, 30, 60]:
        df[f"rv_{w}"] = df["log_ret"].rolling(w).std() * np.sqrt(365)
 
    for w in [7, 21, 50]:
        df[f"sma_{w}"] = c.rolling(w).mean()
    df["ema_12"] = c.ewm(span=12).mean()
    df["ema_26"] = c.ewm(span=26).mean()
    df["macd"]   = df["ema_12"] - df["ema_26"]
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
 
    # Target: forward volatility
    df["target"] = (
        df["log_ret"].shift(-1).rolling(horizon).std().shift(-(horizon - 1))
        * np.sqrt(365)
    )
 
    df.dropna(inplace=True)
    return df
 
FEATURES = [
    "log_ret", "daily_range_pct",
    "rv_7", "rv_14", "rv_30", "rv_60",
    "sma_7", "sma_21", "sma_50", "ema_12", "ema_26",
    "macd", "macd_signal",
    "bb_width", "bb_pct",
    "atr_14",
    "liq_ratio", "volume_sma14", "volume_z",
    "mom_7", "mom_30",
    "dow", "month", "quarter"
]
 
# ── Main Logic ────────────────────────────────────────────────────────────────
if run_btn:
    with st.spinner(f"⏳ Fetching {SYMBOL} data from Yahoo Finance..."):
        raw = yf.download(SYMBOL, period=PERIOD, auto_adjust=True, progress=False)
        if isinstance(raw.columns, pd.MultiIndex):
            raw.columns = raw.columns.get_level_values(0)
 
    if raw.empty or len(raw) < 100:
        st.error("❌ Not enough data fetched. Try a longer period or different symbol.")
        st.stop()
 
    with st.spinner("🔧 Engineering features..."):
        feat_df = add_features(raw, horizon=FORECAST_DAYS)
 
    # ── Train / Test split (80 / 20 temporal)
    split = int(len(feat_df) * 0.8)
    X_train = feat_df.iloc[:split][FEATURES]
    y_train = feat_df.iloc[:split]["target"]
    X_test  = feat_df.iloc[split:][FEATURES]
    y_test  = feat_df.iloc[split:]["target"]
 
    with st.spinner("🤖 Training Random Forest model..."):
        scaler = StandardScaler()
        X_tr_sc = scaler.fit_transform(X_train)
        X_te_sc = scaler.transform(X_test)
 
        model = RandomForestRegressor(
            n_estimators=N_ESTIMATORS, max_depth=12,
            min_samples_leaf=5, n_jobs=-1, random_state=42
        )
        model.fit(X_tr_sc, y_train)
        y_pred = model.predict(X_te_sc)
 
        # Regime classifier
        q33 = np.percentile(y_train, 33)
        q67 = np.percentile(y_train, 67)
        def label(v): return 0 if v < q33 else (1 if v < q67 else 2)
        y_train_cls = y_train.map(label)
        y_test_cls  = y_test.map(label)
 
        clf = RandomForestClassifier(n_estimators=100, max_depth=8, random_state=42, n_jobs=-1)
        clf.fit(X_tr_sc, y_train_cls)
        regime_pred = clf.predict(X_te_sc)
 
    # ── Latest prediction ─────────────────────────────────────────────────────
    latest_X    = scaler.transform(feat_df[FEATURES].iloc[[-1]])
    latest_vol  = model.predict(latest_X)[0]
    latest_reg  = clf.predict(latest_X)[0]
    reg_map     = {0: ("🟢 LOW",    "#22c55e"),
                   1: ("🟡 MEDIUM", "#eab308"),
                   2: ("🔴 HIGH",   "#ef4444")}
    reg_label, reg_color = reg_map[latest_reg]
 
    # ── Metrics ───────────────────────────────────────────────────────────────
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))
    mae  = mean_absolute_error(y_test, y_pred)
    r2   = r2_score(y_test, y_pred)
 
    # ════════════════════ DISPLAY ════════════════════════════════════════════
 
    st.success(f"✅ Model trained on **{len(X_train):,}** rows | Tested on **{len(X_test):,}** rows")
 
    # ── KPI cards
    k1, k2, k3, k4, k5 = st.columns(5)
    k1.metric("📅 Data Points",    f"{len(feat_df):,}")
    k2.metric("📉 RMSE",           f"{rmse:.4f}")
    k3.metric("📉 MAE",            f"{mae:.4f}")
    k4.metric("📈 R² Score",       f"{r2:.4f}")
    k5.metric(f"⚡ Next {FORECAST_DAYS}d Vol", f"{latest_vol:.4f}")
 
    st.markdown("---")
 
    # ── Regime banner
    st.markdown(
        f"""<div style='background:{reg_color}22; border-left:6px solid {reg_color};
        padding:16px 20px; border-radius:8px; margin-bottom:20px;'>
        <h3 style='margin:0; color:{reg_color};'>Volatility Regime: {reg_label}</h3>
        <p style='margin:4px 0 0 0; color:#ccc;'>
        Predicted {FORECAST_DAYS}-day forward annualised volatility:
        <strong style='color:white'>{latest_vol:.4f}</strong>
        &nbsp;|&nbsp; Thresholds — Low &lt; {q33:.4f} &lt; Medium &lt; {q67:.4f} &lt; High
        </p></div>""",
        unsafe_allow_html=True
    )
 
    # ── Row 1: Price chart + Rolling volatility
    col1, col2 = st.columns(2)
 
    with col1:
        st.subheader(f"📊 {SYMBOL} Price History")
        fig, ax = plt.subplots(figsize=(7, 3.5))
        ax.plot(raw.index, raw["Close"], color="#38bdf8", lw=1.2)
        ax.set_ylabel("Price (USD)")
        ax.xaxis.set_major_locator(mdates.YearLocator())
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
        ax.set_facecolor("#0f172a"); fig.patch.set_facecolor("#0f172a")
        ax.tick_params(colors="white"); ax.yaxis.label.set_color("white")
        for spine in ax.spines.values(): spine.set_edgecolor("#334155")
        plt.tight_layout()
        st.pyplot(fig)
        plt.close()
 
    with col2:
        st.subheader("📉 30-Day Rolling Volatility (Annualised)")
        fig, ax = plt.subplots(figsize=(7, 3.5))
        ax.plot(feat_df.index, feat_df["rv_30"], color="#f472b6", lw=1.2)
        ax.axhline(feat_df["rv_30"].mean(), color="#94a3b8", lw=0.8, linestyle="--", label="Mean")
        ax.set_ylabel("Volatility")
        ax.legend(facecolor="#1e293b", labelcolor="white")
        ax.set_facecolor("#0f172a"); fig.patch.set_facecolor("#0f172a")
        ax.tick_params(colors="white"); ax.yaxis.label.set_color("white")
        for spine in ax.spines.values(): spine.set_edgecolor("#334155")
        plt.tight_layout()
        st.pyplot(fig)
        plt.close()
 
    # ── Row 2: Predicted vs Actual + Feature Importance
    col3, col4 = st.columns(2)
 
    with col3:
        st.subheader("🎯 Predicted vs Actual Volatility (Test Set)")
        fig, ax = plt.subplots(figsize=(7, 3.5))
        test_dates = feat_df.iloc[split:].index
        ax.plot(test_dates, y_test.values, label="Actual",    color="#38bdf8", lw=1.2)
        ax.plot(test_dates, y_pred,        label="Predicted", color="#f97316", lw=1.2, linestyle="--")
        ax.legend(facecolor="#1e293b", labelcolor="white")
        ax.set_ylabel("Annualised Volatility")
        ax.set_facecolor("#0f172a"); fig.patch.set_facecolor("#0f172a")
        ax.tick_params(colors="white"); ax.yaxis.label.set_color("white")
        for spine in ax.spines.values(): spine.set_edgecolor("#334155")
        plt.tight_layout()
        st.pyplot(fig)
        plt.close()
 
    with col4:
        st.subheader("🔍 Top 10 Feature Importances")
        imp = pd.Series(model.feature_importances_, index=FEATURES).nlargest(10).sort_values()
        fig, ax = plt.subplots(figsize=(7, 3.5))
        bars = ax.barh(imp.index, imp.values, color="#818cf8", alpha=0.85, edgecolor="none")
        ax.set_xlabel("Importance")
        ax.set_facecolor("#0f172a"); fig.patch.set_facecolor("#0f172a")
        ax.tick_params(colors="white"); ax.xaxis.label.set_color("white")
        ax.yaxis.label.set_color("white")
        for spine in ax.spines.values(): spine.set_edgecolor("#334155")
        plt.tight_layout()
        st.pyplot(fig)
        plt.close()
 
    # ── Row 3: Bollinger Bands
    st.subheader("📐 Bollinger Bands (Last 120 Days)")
    last120 = feat_df.tail(120)
    fig, ax = plt.subplots(figsize=(14, 4))
    ax.plot(last120.index, last120.index.map(lambda d: raw.loc[d, "Close"] if d in raw.index else np.nan),
            color="#38bdf8", lw=1.5, label="Close")
    ax.plot(last120.index, last120["bb_upper"], color="#f472b6", lw=0.8, linestyle="--", label="Upper Band")
    ax.plot(last120.index, last120["bb_mid"],   color="#94a3b8", lw=0.8, linestyle="--", label="Middle Band")
    ax.plot(last120.index, last120["bb_lower"], color="#4ade80", lw=0.8, linestyle="--", label="Lower Band")
    ax.fill_between(last120.index, last120["bb_upper"], last120["bb_lower"], alpha=0.05, color="#818cf8")
    ax.legend(facecolor="#1e293b", labelcolor="white", ncol=4)
    ax.set_facecolor("#0f172a"); fig.patch.set_facecolor("#0f172a")
    ax.tick_params(colors="white")
    for spine in ax.spines.values(): spine.set_edgecolor("#334155")
    plt.tight_layout()
    st.pyplot(fig)
    plt.close()
 
    # ── Regime history table
    st.subheader("📋 Recent Predictions (Last 10 Test Days)")
    recent = feat_df.iloc[split:].tail(10)[["rv_7", "rv_30", "bb_width", "atr_14"]].copy()
    recent["Predicted Vol"] = model.predict(scaler.transform(feat_df.iloc[split:][FEATURES]))[-10:]
    recent["Regime"] = [reg_map[r][0] for r in clf.predict(
        scaler.transform(feat_df.iloc[split:][FEATURES]))[-10:]]
    recent.index = recent.index.date
    recent.columns = ["RV-7", "RV-30", "BB Width", "ATR-14", "Pred Vol", "Regime"]
    st.dataframe(recent.style.format({
        "RV-7":".4f","RV-30":".4f","BB Width":".4f","ATR-14":".4f","Pred Vol":".4f"
    }), use_container_width=True)
 
    st.markdown("---")
    st.caption("Built with ❤️ using Streamlit · yfinance · scikit-learn · Random Forest")
 
else:
    # ── Landing state
    st.info("👈 Select a cryptocurrency from the sidebar and click **Run Prediction** to start.")
    c1, c2, c3 = st.columns(3)
    c1.markdown("### 🔧 Features Used\n- OHLCV data via yfinance\n- Rolling volatility (7/14/30/60d)\n- Bollinger Bands & ATR\n- MACD, Momentum, Volume Z-score")
    c2.markdown("### 🤖 Models\n- Random Forest Regressor\n- Random Forest Classifier\n- StandardScaler pipeline\n- TimeSeriesSplit evaluation")
    c3.markdown("### 📊 Outputs\n- Predicted forward volatility\n- Volatility regime (Low/Med/High)\n- Feature importance chart\n- Predicted vs Actual plot")