# 📈 Cryptocurrency Volatility Predictor

A Machine Learning web application that predicts **7-day forward annualised volatility** of cryptocurrencies using historical OHLCV data.

🚀 **Live Demo:** [Click Here to Open App](https://share.streamlit.io)

---

## 📌 Problem Statement

Cryptocurrency markets are highly volatile. Understanding and forecasting this volatility is crucial for:
- Risk Management
- Portfolio Allocation
- Developing Trading Strategies

This project builds a Machine Learning model to predict cryptocurrency volatility levels based on historical market data such as OHLC (Open, High, Low, Close) prices, trading volume, and market capitalization.

---

## 🗂️ Project Structure

```
📦 Cryptocurrency-Volatility-Predictor/
│
├── 📄 app.py                              # Streamlit Web App
├── 📓 Crypto_Volatility_Prediction.ipynb  # Full ML Pipeline Notebook
├── 📄 requirements.txt                    # Python Dependencies
├── 📄 runtime.txt                         # Python Version (3.10.11)
├── 📄 README.md                           # Project Documentation
│
├── 🤖 crypto_vol_pipeline.pkl             # Trained Pipeline (Scaler + Model)
├── 🤖 vol_regime_classifier.pkl           # Volatility Regime Classifier
├── 🤖 random_forest_model.pkl             # Random Forest Model
├── 🤖 xgboost_model.pkl                   # XGBoost Model
├── 🤖 xgboost_tuned_model.pkl             # Tuned XGBoost Model
├── 🤖 lgbm_model.pkl                      # LightGBM Model
├── 🤖 feature_scaler.pkl                  # StandardScaler
└── 📄 model_metadata.json                 # Model Info & Metrics
```

---

## 🔧 Tech Stack

| Category | Tools |
|----------|-------|
| **Language** | Python 3.10.11 |
| **Data Fetching** | yfinance |
| **Data Processing** | Pandas, NumPy |
| **Machine Learning** | Scikit-learn, XGBoost, LightGBM |
| **Visualisation** | Matplotlib, Seaborn |
| **Web App** | Streamlit |
| **Model Saving** | Joblib |

---

## 📊 Dataset Information

- **Source:** Yahoo Finance (via yfinance)
- **Cryptocurrencies:** 50+ coins (BTC, ETH, BNB, SOL, ADA, XRP, DOGE, etc.)
- **Period:** 2019 – 2024
- **Frequency:** Daily
- **Features:** Open, High, Low, Close, Volume, Market Cap

---

## ⚙️ Feature Engineering

| Feature Family | Features |
|----------------|----------|
| **Returns** | log_return, daily_range_pct |
| **Rolling Volatility** | rv_7, rv_14, rv_30, rv_60 |
| **Moving Averages** | sma_7, sma_21, sma_50, ema_12, ema_26 |
| **MACD** | macd, macd_signal |
| **Bollinger Bands** | bb_upper, bb_lower, bb_width, bb_pct |
| **ATR** | atr_14 |
| **Liquidity** | liq_ratio, volume_sma14, volume_z |
| **Momentum** | mom_7, mom_30 |
| **Calendar** | day_of_week, month, quarter |

---

## 🤖 Models Used

| Model | Description |
|-------|-------------|
| Linear Regression | Baseline model |
| Random Forest | Ensemble of decision trees |
| XGBoost | Gradient boosted trees |
| XGBoost (Tuned) | Hyperparameter optimised XGBoost |
| LightGBM | Fast gradient boosting |
| RF Classifier | Volatility Regime classifier (Low / Medium / High) |

---

## 📈 Model Evaluation Metrics

| Metric | Description |
|--------|-------------|
| **RMSE** | Root Mean Squared Error |
| **MAE** | Mean Absolute Error |
| **R² Score** | Coefficient of Determination |

---

## 🌐 Streamlit App Features

- 📊 **Price History Chart** — Interactive closing price visualization
- 📉 **Rolling Volatility Chart** — 30-day annualised volatility trend
- 🎯 **Predicted vs Actual** — Model performance on test data
- 🔍 **Feature Importance** — Top 10 most impactful features
- 📐 **Bollinger Bands** — Last 120 days price bands
- 🟢🟡🔴 **Regime Banner** — Low / Medium / High volatility prediction
- 📋 **Recent Predictions Table** — Last 10 test days with regime labels

---

## 🚀 How to Run Locally

**1. Clone the repository**
```bash
git clone https://github.com/premchavan772005-spec/-Cryptocurrency-Volatility-Predictor.git
cd -Cryptocurrency-Volatility-Predictor
```

**2. Install dependencies**
```bash
pip install -r requirements.txt
```

**3. Run the Streamlit app**
```bash
streamlit run app.py
```

**4. Open in browser**
```
http://localhost:8501
```

---

## 📓 Run the Notebook

Open `Crypto_Volatility_Prediction.ipynb` in Jupyter or VS Code and run all cells top to bottom.

```bash
jupyter notebook Crypto_Volatility_Prediction.ipynb
```

---

## 📦 Project Development Steps

1. ✅ **Data Collection** — Fetch historical OHLCV data via yfinance
2. ✅ **Data Preprocessing** — Handle missing values, normalize features
3. ✅ **Exploratory Data Analysis** — Trends, correlations, distributions
4. ✅ **Feature Engineering** — 24 features including Bollinger Bands, ATR, MACD
5. ✅ **Model Selection** — Random Forest, XGBoost, LightGBM
6. ✅ **Model Training** — Temporal train/val/test split
7. ✅ **Model Evaluation** — RMSE, MAE, R² metrics
8. ✅ **Hyperparameter Tuning** — RandomizedSearchCV with TimeSeriesSplit
9. ✅ **Regime Classification** — Low / Medium / High volatility labels
10. ✅ **Deployment** — Streamlit Cloud deployment

---

## 👨‍💻 Author

**Prem Chavan**
- GitHub: [@premchavan772005-spec](https://github.com/premchavan772005-spec)

---

## 📄 License

This project is for **educational purposes** as part of a Machine Learning course project.

---

⭐ **If you found this project helpful, please give it a star on GitHub!** ⭐
