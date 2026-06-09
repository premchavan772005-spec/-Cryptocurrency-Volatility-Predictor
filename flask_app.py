"""
Crypto Volatility Predictor — Flask UI
Google Material Design 3 professional dashboard.
"""

import os
import logging
import requests
from flask import Flask, render_template_string, jsonify, request

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

app = Flask(__name__)
FASTAPI_URL = os.getenv("FASTAPI_URL", "http://localhost:8000").rstrip("/")

# ── Proxy helpers ─────────────────────────────────────────────────────────────
def _call(method, path, **kwargs):
    url = f"{FASTAPI_URL}{path}"
    try:
        r = getattr(requests, method)(url, timeout=60, **kwargs)
        return r.json(), r.status_code
    except requests.exceptions.ConnectionError:
        return {"error": "FastAPI service unreachable", "detail": url}, 503
    except Exception as e:
        return {"error": str(e)}, 500

# ── API proxy routes ──────────────────────────────────────────────────────────
@app.route("/api/health")
def api_health():
    data, status = _call("get", "/health")
    return jsonify(data), status

@app.route("/api/predict", methods=["POST"])
def api_predict():
    data, status = _call("post", "/predict", json=request.get_json(force=True))
    return jsonify(data), status

@app.route("/api/batch", methods=["POST"])
def api_batch():
    data, status = _call("post", "/batch_predict", json=request.get_json(force=True))
    return jsonify(data), status

@app.route("/api/symbols")
def api_symbols():
    return jsonify({"symbols": [
        "BTC","ETH","BNB","SOL","XRP","ADA","DOGE",
        "DOT","MATIC","LTC","AVAX","LINK","UNI","XLM","ATOM"
    ]})

# ── HTML ──────────────────────────────────────────────────────────────────────
HTML = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>CryptoVol · Volatility Intelligence Platform</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Google+Sans:wght@400;500;700&family=Google+Sans+Mono&family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@24,400,0,0&display=swap" rel="stylesheet">
<style>
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
:root{
  --blue:#1a73e8;--blue-hover:#1557b0;--blue-light:#e8f0fe;
  --green:#1e8e3e;--green-light:#e6f4ea;
  --red:#d93025;--red-light:#fce8e6;
  --amber:#f9ab00;--amber-light:#fef7e0;
  --purple:#8430ce;--purple-light:#f3e8fd;
  --surface:#fff;--surface-2:#f8f9fa;--surface-3:#f1f3f4;
  --border:#dadce0;--text:#202124;--text-2:#5f6368;--text-3:#80868b;
  --sidebar-w:240px;--topbar-h:64px;
  --shadow-sm:0 1px 2px rgba(60,64,67,.3),0 1px 3px 1px rgba(60,64,67,.15);
  --radius:8px;--radius-lg:12px;
  --font:"Google Sans",sans-serif;--mono:"Google Sans Mono",monospace;
}
body{font-family:var(--font);background:var(--surface-2);color:var(--text);min-height:100vh;display:flex;flex-direction:column}
#topbar{position:fixed;top:0;left:0;right:0;height:var(--topbar-h);background:var(--surface);border-bottom:1px solid var(--border);display:flex;align-items:center;padding:0 24px;gap:16px;z-index:100;box-shadow:var(--shadow-sm)}
#topbar .logo{display:flex;align-items:center;gap:10px;text-decoration:none;margin-right:auto}
#topbar .logo-text{font-size:18px;font-weight:700;color:var(--text)}
#topbar .logo-sub{font-size:12px;color:var(--text-2);margin-left:4px}
#api-badge{display:flex;align-items:center;gap:6px;padding:6px 14px;border-radius:20px;font-size:13px;font-weight:500;cursor:pointer;border:1px solid var(--border);transition:all .2s}
#api-badge.online{background:var(--green-light);color:var(--green);border-color:#a8d5b5}
#api-badge.offline{background:var(--red-light);color:var(--red);border-color:#f5b8b5}
#api-badge .dot{width:8px;height:8px;border-radius:50%;background:currentColor}
.avatar{width:36px;height:36px;border-radius:50%;background:var(--blue);color:#fff;display:flex;align-items:center;justify-content:center;font-size:14px;font-weight:600;margin-left:8px}
#layout{display:flex;margin-top:var(--topbar-h);min-height:calc(100vh - var(--topbar-h))}
#sidebar{width:var(--sidebar-w);flex-shrink:0;background:var(--surface);border-right:1px solid var(--border);padding:12px 0;position:sticky;top:var(--topbar-h);height:calc(100vh - var(--topbar-h));overflow-y:auto}
.nav-section{padding:8px 16px 4px;font-size:11px;font-weight:600;color:var(--text-3);letter-spacing:.8px;text-transform:uppercase}
.nav-item{display:flex;align-items:center;gap:12px;padding:10px 16px;cursor:pointer;font-size:14px;color:var(--text-2);transition:background .15s,color .15s;border:none;background:none;width:100%;text-align:left;position:relative}
.nav-item:hover{background:var(--surface-3);color:var(--text)}
.nav-item.active{background:var(--blue-light);color:var(--blue);font-weight:500}
.nav-item.active::before{content:'';position:absolute;left:0;top:4px;bottom:4px;width:3px;background:var(--blue);border-radius:0 2px 2px 0}
.nav-item .material-symbols-outlined{font-size:20px}
#main{flex:1;padding:24px;max-width:1100px}
.page-header{margin-bottom:24px}
.page-header h1{font-size:22px;font-weight:500;color:var(--text);margin-bottom:4px}
.page-header p{font-size:14px;color:var(--text-2)}
.stat-strip{display:grid;grid-template-columns:repeat(auto-fit,minmax(160px,1fr));gap:16px;margin-bottom:24px}
.stat-card{background:var(--surface);border:1px solid var(--border);border-radius:var(--radius-lg);padding:16px 20px;display:flex;flex-direction:column;gap:4px}
.stat-label{font-size:11px;font-weight:600;color:var(--text-3);text-transform:uppercase;letter-spacing:.6px}
.stat-value{font-size:22px;font-weight:700;color:var(--text);font-family:var(--mono)}
.stat-sub{font-size:12px;color:var(--text-2)}
.card{background:var(--surface);border:1px solid var(--border);border-radius:var(--radius-lg);overflow:hidden;margin-bottom:20px;box-shadow:var(--shadow-sm)}
.card-header{padding:16px 20px;border-bottom:1px solid var(--border);display:flex;align-items:center;gap:10px}
.card-header h2{font-size:15px;font-weight:500;color:var(--text);flex:1}
.card-body{padding:20px}
.form-row{display:grid;grid-template-columns:1fr 1fr 1fr;gap:16px;margin-bottom:16px}
.form-group{display:flex;flex-direction:column;gap:6px}
label{font-size:13px;font-weight:500;color:var(--text-2)}
select,input{padding:10px 14px;border:1px solid var(--border);border-radius:var(--radius);font-size:14px;font-family:var(--font);color:var(--text);background:var(--surface);outline:none;transition:border-color .2s,box-shadow .2s}
select:focus,input:focus{border-color:var(--blue);box-shadow:0 0 0 3px rgba(26,115,232,.15)}
.btn{display:inline-flex;align-items:center;gap:8px;padding:10px 20px;border-radius:var(--radius);font-size:14px;font-weight:500;cursor:pointer;border:none;transition:all .2s;font-family:var(--font)}
.btn-primary{background:var(--blue);color:#fff}
.btn-primary:hover{background:var(--blue-hover);box-shadow:var(--shadow-sm)}
.btn-outline{background:none;color:var(--blue);border:1px solid var(--blue)}
.btn-outline:hover{background:var(--blue-light)}
.btn:disabled{opacity:.6;cursor:not-allowed}
.btn .material-symbols-outlined{font-size:18px}
#result-panel{display:none}
.result-hero{display:flex;align-items:center;gap:20px;padding:20px;border-radius:var(--radius);margin-bottom:20px}
.result-hero.low{background:var(--green-light)}
.result-hero.medium{background:var(--amber-light)}
.result-hero.high{background:var(--red-light)}
.result-hero.extreme{background:var(--purple-light)}
.vol-number{font-size:52px;font-weight:700;font-family:var(--mono)}
.vol-number.low{color:var(--green)}
.vol-number.medium{color:var(--amber)}
.vol-number.high{color:var(--red)}
.vol-number.extreme{color:var(--purple)}
.result-meta{flex:1}
.result-meta h3{font-size:18px;font-weight:600;margin-bottom:4px}
.result-meta p{font-size:14px;color:var(--text-2);margin-bottom:2px}
.risk-chip{display:inline-block;padding:4px 12px;border-radius:20px;font-size:12px;font-weight:600;text-transform:uppercase;letter-spacing:.5px}
.risk-chip.low{background:var(--green);color:#fff}
.risk-chip.medium{background:var(--amber);color:#fff}
.risk-chip.high{background:var(--red);color:#fff}
.risk-chip.extreme{background:var(--purple);color:#fff}
.metrics-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:12px}
.metric-box{background:var(--surface-2);border:1px solid var(--border);border-radius:var(--radius);padding:14px 16px}
.metric-box .label{font-size:12px;color:var(--text-3);margin-bottom:4px}
.metric-box .value{font-size:18px;font-weight:600;font-family:var(--mono);color:var(--text)}
.batch-grid{display:grid;gap:12px}
.batch-row{display:grid;grid-template-columns:40px 80px 1fr 100px 130px 80px;align-items:center;gap:12px;padding:14px 16px;background:var(--surface);border:1px solid var(--border);border-radius:var(--radius);transition:box-shadow .15s}
.batch-row:hover{box-shadow:var(--shadow-sm)}
.vol-bar-track{background:var(--surface-3);border-radius:4px;height:6px;overflow:hidden}
.vol-bar-fill{height:100%;border-radius:4px;transition:width .8s ease}
.vol-bar-fill.low{background:var(--green)}
.vol-bar-fill.medium{background:var(--amber)}
.vol-bar-fill.high{background:var(--red)}
.vol-bar-fill.extreme{background:var(--purple)}
.tab-list{display:flex;border-bottom:1px solid var(--border);margin-bottom:20px}
.tab{padding:12px 20px;font-size:14px;font-weight:500;color:var(--text-2);cursor:pointer;border-bottom:3px solid transparent;margin-bottom:-1px;transition:all .2s;background:none;border-top:none;border-left:none;border-right:none}
.tab:hover{color:var(--blue)}
.tab.active{color:var(--blue);border-bottom-color:var(--blue)}
.tab-pane{display:none}
.tab-pane.active{display:block}
.status-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:16px}
.status-box{border:1px solid var(--border);border-radius:var(--radius-lg);padding:20px;display:flex;flex-direction:column;gap:8px}
.status-box h3{font-size:14px;font-weight:600;color:var(--text-2)}
.status-indicator{display:flex;align-items:center;gap:8px;font-size:16px;font-weight:600}
.status-indicator .dot{width:10px;height:10px;border-radius:50%}
.dot-green{background:var(--green)}
.dot-red{background:var(--red)}
.dot-amber{background:var(--amber)}
.status-detail{font-size:12px;color:var(--text-3)}
.spinner{width:40px;height:40px;border:3px solid var(--border);border-top-color:var(--blue);border-radius:50%;animation:spin .8s linear infinite;margin:32px auto;display:block}
@keyframes spin{to{transform:rotate(360deg)}}
.loading-msg{text-align:center;color:var(--text-2);font-size:14px;margin-top:8px}
.alert{padding:12px 16px;border-radius:var(--radius);font-size:14px;margin-bottom:16px;display:flex;align-items:center;gap:8px}
.alert-error{background:var(--red-light);color:var(--red);border:1px solid #f5b8b5}
pre.json-out{background:#1e1e2e;color:#cdd6f4;padding:16px;border-radius:var(--radius);font-family:var(--mono);font-size:12px;overflow-x:auto;max-height:400px;overflow-y:auto}
@media(max-width:768px){#sidebar{display:none}.form-row{grid-template-columns:1fr}.metrics-grid{grid-template-columns:1fr 1fr}.status-grid{grid-template-columns:1fr}}
</style>
</head>
<body>

<header id="topbar">
  <a href="/" class="logo">
    <svg width="32" height="32" viewBox="0 0 32 32" fill="none"><rect width="32" height="32" rx="8" fill="#1a73e8"/><path d="M8 20 L16 8 L24 20" stroke="white" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/><circle cx="16" cy="22" r="3" fill="white"/></svg>
    <span class="logo-text">CryptoVol</span>
    <span class="logo-sub">Volatility Intelligence</span>
  </a>
  <div id="api-badge" class="offline" onclick="checkHealth()" title="Click to refresh">
    <span class="dot"></span>
    <span id="api-status-text">Checking…</span>
  </div>
  <div class="avatar">CV</div>
</header>

<div id="layout">
<nav id="sidebar">
  <div class="nav-section">Predict</div>
  <button class="nav-item active" onclick="showPage('single',this)">
    <span class="material-symbols-outlined">monitoring</span>Single Coin
  </button>
  <button class="nav-item" onclick="showPage('batch',this)">
    <span class="material-symbols-outlined">grid_view</span>Batch Analysis
  </button>
  <div class="nav-section" style="margin-top:12px">Tools</div>
  <button class="nav-item" onclick="showPage('explorer',this)">
    <span class="material-symbols-outlined">terminal</span>API Explorer
  </button>
  <button class="nav-item" onclick="showPage('health',this)">
    <span class="material-symbols-outlined">health_and_safety</span>Health Monitor
  </button>
</nav>

<main id="main">

  <!-- SINGLE COIN -->
  <div id="page-single">
    <div class="page-header">
      <h1>Single Coin Volatility Prediction</h1>
      <p>Fetch live market data and predict future volatility using pre-trained ML models.</p>
    </div>
    <div class="stat-strip">
      <div class="stat-card"><span class="stat-label">Model Type</span><span class="stat-value" style="font-size:16px">ML Ensemble</span><span class="stat-sub">Random Forest + XGBoost</span></div>
      <div class="stat-card"><span class="stat-label">Features</span><span class="stat-value">16</span><span class="stat-sub">Technical indicators</span></div>
      <div class="stat-card"><span class="stat-label">Coins Supported</span><span class="stat-value">15</span><span class="stat-sub">Live via yfinance</span></div>
      <div class="stat-card"><span class="stat-label">Data Source</span><span class="stat-value" style="font-size:16px">Yahoo Finance</span><span class="stat-sub">Real-time OHLCV</span></div>
    </div>
    <div class="card">
      <div class="card-header">
        <span class="material-symbols-outlined" style="color:var(--blue)">tune</span>
        <h2>Prediction Parameters</h2>
      </div>
      <div class="card-body">
        <div class="form-row">
          <div class="form-group">
            <label>Cryptocurrency</label>
            <select id="symbol">
              <option value="BTC">Bitcoin (BTC)</option>
              <option value="ETH">Ethereum (ETH)</option>
              <option value="BNB">BNB Chain (BNB)</option>
              <option value="SOL">Solana (SOL)</option>
              <option value="XRP">XRP (XRP)</option>
              <option value="ADA">Cardano (ADA)</option>
              <option value="DOGE">Dogecoin (DOGE)</option>
              <option value="DOT">Polkadot (DOT)</option>
              <option value="MATIC">Polygon (MATIC)</option>
              <option value="LTC">Litecoin (LTC)</option>
              <option value="AVAX">Avalanche (AVAX)</option>
              <option value="LINK">Chainlink (LINK)</option>
              <option value="UNI">Uniswap (UNI)</option>
              <option value="XLM">Stellar (XLM)</option>
              <option value="ATOM">Cosmos (ATOM)</option>
            </select>
          </div>
          <div class="form-group">
            <label>Historical Period</label>
            <select id="period">
              <option value="6mo">6 Months</option>
              <option value="1y">1 Year</option>
              <option value="2y" selected>2 Years</option>
              <option value="3y">3 Years</option>
              <option value="5y">5 Years</option>
            </select>
          </div>
          <div class="form-group">
            <label>Forecast Horizon</label>
            <select id="horizon">
              <option value="7">7 Days</option>
              <option value="14">14 Days</option>
              <option value="30" selected>30 Days</option>
              <option value="60">60 Days</option>
              <option value="90">90 Days</option>
            </select>
          </div>
        </div>
        <button class="btn btn-primary" id="predict-btn" onclick="runPredict()">
          <span class="material-symbols-outlined">bolt</span>Run Prediction
        </button>
      </div>
    </div>
    <div id="predict-loading" style="display:none"><div class="spinner"></div><p class="loading-msg">Fetching live data & running model…</p></div>
    <div id="predict-error" class="alert alert-error" style="display:none"></div>
    <div id="result-panel" class="card">
      <div class="card-header">
        <span class="material-symbols-outlined" style="color:var(--blue)">insights</span>
        <h2>Prediction Result</h2>
        <span id="result-timestamp" style="font-size:12px;color:var(--text-3);margin-left:auto"></span>
      </div>
      <div class="card-body">
        <div class="result-hero" id="result-hero">
          <div><div class="vol-number" id="vol-number"></div><div style="font-size:13px;margin-top:4px;color:var(--text-2)">Predicted Annualised Volatility</div></div>
          <div class="result-meta">
            <h3 id="result-title"></h3>
            <p id="result-sub"></p>
            <p id="result-ci"></p>
            <span class="risk-chip" id="risk-chip"></span>
          </div>
        </div>
        <div class="metrics-grid" id="metrics-grid"></div>
      </div>
    </div>
  </div>

  <!-- BATCH -->
  <div id="page-batch" style="display:none">
    <div class="page-header"><h1>Batch Volatility Analysis</h1><p>Compare predicted volatility across multiple coins.</p></div>
    <div class="card">
      <div class="card-header"><span class="material-symbols-outlined" style="color:var(--blue)">checklist</span><h2>Select Coins</h2></div>
      <div class="card-body">
        <div style="display:flex;flex-wrap:wrap;gap:10px;margin-bottom:16px" id="coin-chips"></div>
        <div class="form-row" style="grid-template-columns:1fr 1fr">
          <div class="form-group"><label>Historical Period</label><select id="batch-period"><option value="1y">1 Year</option><option value="2y" selected>2 Years</option><option value="5y">5 Years</option></select></div>
          <div class="form-group"><label>Forecast Horizon</label><select id="batch-horizon"><option value="7">7 Days</option><option value="30" selected>30 Days</option><option value="90">90 Days</option></select></div>
        </div>
        <button class="btn btn-primary" onclick="runBatch()"><span class="material-symbols-outlined">analytics</span>Analyse All Selected</button>
      </div>
    </div>
    <div id="batch-loading" style="display:none"><div class="spinner"></div><p class="loading-msg">Fetching live data for each coin…</p></div>
    <div id="batch-error" class="alert alert-error" style="display:none"></div>
    <div id="batch-results" class="batch-grid" style="margin-top:16px"></div>
  </div>

  <!-- API EXPLORER -->
  <div id="page-explorer" style="display:none">
    <div class="page-header"><h1>API Explorer</h1><p>Test FastAPI endpoints directly from the browser.</p></div>
    <div class="card">
      <div class="card-header"><h2>Available Endpoints</h2></div>
      <div class="card-body">
        <div class="tab-list">
          <button class="tab active" onclick="showTab(this,'tab-predict')">POST /predict</button>
          <button class="tab" onclick="showTab(this,'tab-batch')">POST /batch_predict</button>
          <button class="tab" onclick="showTab(this,'tab-health')">GET /health</button>
        </div>
        <div class="tab-pane active" id="tab-predict">
          <div class="form-row">
            <div class="form-group"><label>Symbol</label><input id="ex-symbol" value="ETH"></div>
            <div class="form-group"><label>Period</label><input id="ex-period" value="2y"></div>
            <div class="form-group"><label>Horizon Days</label><input id="ex-horizon" type="number" value="30"></div>
          </div>
          <button class="btn btn-outline" onclick="explorerPredict()"><span class="material-symbols-outlined">send</span>Send Request</button>
          <div style="margin-top:16px"><div style="font-size:12px;color:var(--text-3);margin-bottom:6px">Response</div><pre class="json-out" id="ex-out-predict">// Response will appear here</pre></div>
        </div>
        <div class="tab-pane" id="tab-batch">
          <div class="form-group" style="margin-bottom:16px"><label>Symbols (comma-separated)</label><input id="ex-batch-syms" value="BTC,ETH,SOL,ADA"></div>
          <button class="btn btn-outline" onclick="explorerBatch()"><span class="material-symbols-outlined">send</span>Send Request</button>
          <div style="margin-top:16px"><pre class="json-out" id="ex-out-batch">// Response will appear here</pre></div>
        </div>
        <div class="tab-pane" id="tab-health">
          <button class="btn btn-outline" onclick="explorerHealth()"><span class="material-symbols-outlined">send</span>Send Request</button>
          <div style="margin-top:16px"><pre class="json-out" id="ex-out-health">// Response will appear here</pre></div>
        </div>
      </div>
    </div>
  </div>

  <!-- HEALTH -->
  <div id="page-health" style="display:none">
    <div class="page-header"><h1>Health Monitor</h1><p>Real-time status of all system components.</p></div>
    <div class="status-grid" id="status-grid">
      <div class="status-box"><h3>FastAPI Backend</h3><div class="status-indicator" id="h-fastapi"><span class="dot dot-amber"></span>Checking…</div><div class="status-detail" id="h-fastapi-detail">—</div></div>
      <div class="status-box"><h3>Flask Proxy (this app)</h3><div class="status-indicator"><span class="dot dot-green"></span>Online</div><div class="status-detail">Running on port 5000</div></div>
      <div class="status-box"><h3>ML Models</h3><div class="status-indicator" id="h-models"><span class="dot dot-amber"></span>Checking…</div><div class="status-detail" id="h-models-detail">—</div></div>
    </div>
    <div class="card" style="margin-top:20px">
      <div class="card-header"><h2>Raw Health Response</h2>
        <button class="btn btn-outline" style="padding:6px 14px;font-size:13px;margin-left:auto" onclick="refreshHealth()"><span class="material-symbols-outlined" style="font-size:16px">refresh</span>Refresh</button>
      </div>
      <div class="card-body"><pre class="json-out" id="health-raw">// Click Refresh to load</pre></div>
    </div>
  </div>

</main>
</div>

<script>
const COINS = ["BTC","ETH","BNB","SOL","XRP","ADA","DOGE","DOT","MATIC","LTC","AVAX","LINK","UNI","XLM","ATOM"];
let selectedCoins = new Set(["BTC","ETH","SOL","BNB","XRP"]);

function showPage(name, btn) {
  document.querySelectorAll('[id^="page-"]').forEach(p => p.style.display='none');
  document.getElementById('page-'+name).style.display='block';
  document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));
  if(btn) btn.classList.add('active');
  if(name==='health') refreshHealth();
}

function showTab(btn, paneId) {
  document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
  document.querySelectorAll('.tab-pane').forEach(p => p.classList.remove('active'));
  btn.classList.add('active');
  document.getElementById(paneId).classList.add('active');
}

function buildChips() {
  document.getElementById('coin-chips').innerHTML = COINS.map(c => `
    <label style="display:inline-flex;align-items:center;gap:6px;padding:7px 14px;border-radius:20px;cursor:pointer;font-size:13px;font-weight:500;transition:all .2s;
      background:${selectedCoins.has(c)?'var(--blue)':'var(--surface-3)'};
      color:${selectedCoins.has(c)?'#fff':'var(--text-2)'};
      border:1px solid ${selectedCoins.has(c)?'var(--blue)':'var(--border)'}">
      <input type="checkbox" style="display:none" ${selectedCoins.has(c)?'checked':''} onchange="toggleCoin('${c}',this)"> ${c}
    </label>`).join('');
}

function toggleCoin(c) { selectedCoins.has(c)?selectedCoins.delete(c):selectedCoins.add(c); buildChips(); }

function riskOf(v){if(v<0.02)return'low';if(v<0.04)return'medium';if(v<0.07)return'high';return'extreme';}
function volPct(v){return(v*100).toFixed(2)+'%';}

async function checkHealth() {
  const badge=document.getElementById('api-badge'),txt=document.getElementById('api-status-text');
  txt.textContent='Checking…';
  try{
    const r=await fetch('/api/health');const d=await r.json();
    const ok=r.ok&&d.status==='healthy';
    badge.className=ok?'online':'offline';
    txt.textContent=ok?'API Online':'API Error';
  }catch{badge.className='offline';txt.textContent='API Offline';}
}

async function refreshHealth() {
  const raw=document.getElementById('health-raw'),fa=document.getElementById('h-fastapi'),
        fad=document.getElementById('h-fastapi-detail'),hm=document.getElementById('h-models'),
        hmd=document.getElementById('h-models-detail');
  raw.textContent='Loading…';
  try{
    const r=await fetch('/api/health');const d=await r.json();
    raw.textContent=JSON.stringify(d,null,2);
    if(r.ok&&d.status==='healthy'){
      fa.innerHTML='<span class="dot dot-green"></span>Online';
      fad.textContent=`Responding at ${new Date().toLocaleTimeString()}`;
      const n=d.models_found??0;
      hm.innerHTML=`<span class="dot ${n>0?'dot-green':'dot-red'}"></span>${n>0?n+' model(s) loaded':'No models found'}`;
      hmd.textContent=(d.model_names||[]).join(', ')||'—';
    }else{fa.innerHTML='<span class="dot dot-red"></span>Error';fad.textContent=d.detail||d.error||'Unknown';}
  }catch(e){raw.textContent='// Connection refused';fa.innerHTML='<span class="dot dot-red"></span>Offline';fad.textContent=e.message;}
}

async function runPredict() {
  const btn=document.getElementById('predict-btn'),ld=document.getElementById('predict-loading'),
        err=document.getElementById('predict-error'),res=document.getElementById('result-panel');
  err.style.display='none';res.style.display='none';ld.style.display='block';btn.disabled=true;
  try{
    const r=await fetch('/api/predict',{method:'POST',headers:{'Content-Type':'application/json'},
      body:JSON.stringify({symbol:document.getElementById('symbol').value,
        period:document.getElementById('period').value,
        horizon_days:parseInt(document.getElementById('horizon').value)})});
    const d=await r.json();
    if(!r.ok)throw new Error(d.detail||d.error||`HTTP ${r.status}`);
    renderResult(d);
  }catch(e){err.style.display='flex';err.innerHTML=`<span class="material-symbols-outlined">error</span> ${e.message}`;}
  finally{ld.style.display='none';btn.disabled=false;}
}

function renderResult(d) {
  const vol=d.predicted_volatility,risk=d.risk_level||riskOf(vol),panel=document.getElementById('result-panel'),hero=document.getElementById('result-hero');
  document.getElementById('vol-number').textContent=volPct(vol);
  document.getElementById('vol-number').className=`vol-number ${risk}`;
  hero.className=`result-hero ${risk}`;
  document.getElementById('result-title').textContent=`${d.symbol} — ${d.horizon_days}-Day Forecast`;
  document.getElementById('result-sub').textContent=`Realised 30d vol: ${volPct(d.realized_volatility||0)}`;
  const ci=d.confidence_interval||{};
  document.getElementById('result-ci').textContent=ci.low?`95% CI: ${volPct(ci.low)} – ${volPct(ci.high)}`:'';
  document.getElementById('risk-chip').textContent=risk.toUpperCase()+' RISK';
  document.getElementById('risk-chip').className=`risk-chip ${risk}`;
  document.getElementById('result-timestamp').textContent=new Date().toLocaleTimeString();
  document.getElementById('metrics-grid').innerHTML=`
    <div class="metric-box"><div class="label">Predicted Vol</div><div class="value">${volPct(vol)}</div></div>
    <div class="metric-box"><div class="label">Realised Vol (30d)</div><div class="value">${volPct(d.realized_volatility||0)}</div></div>
    <div class="metric-box"><div class="label">Risk Level</div><div class="value">${risk.toUpperCase()}</div></div>
    <div class="metric-box"><div class="label">Forecast Horizon</div><div class="value">${d.horizon_days}d</div></div>
    <div class="metric-box"><div class="label">Data Points</div><div class="value">${d.data_points||'—'}</div></div>
    <div class="metric-box"><div class="label">Features</div><div class="value">${d.features_used||16}</div></div>`;
  panel.style.display='block';
}

async function runBatch() {
  if(selectedCoins.size===0)return alert('Select at least one coin');
  const ld=document.getElementById('batch-loading'),err=document.getElementById('batch-error'),res=document.getElementById('batch-results');
  err.style.display='none';res.innerHTML='';ld.style.display='block';
  try{
    const r=await fetch('/api/batch',{method:'POST',headers:{'Content-Type':'application/json'},
      body:JSON.stringify({symbols:[...selectedCoins],period:document.getElementById('batch-period').value,
        horizon_days:parseInt(document.getElementById('batch-horizon').value)})});
    const d=await r.json();
    if(!r.ok)throw new Error(d.detail||d.error||`HTTP ${r.status}`);
    const results=d.results||[];
    const maxVol=Math.max(...results.map(r=>r.predicted_volatility),0.01);
    res.innerHTML=results.map((r,i)=>{
      const risk=r.risk_level||riskOf(r.predicted_volatility),pct=(r.predicted_volatility/maxVol*100).toFixed(1);
      return`<div class="batch-row">
        <span style="font-size:13px;font-weight:600;color:var(--text-3)">${i+1}</span>
        <span style="font-size:16px;font-weight:700;font-family:var(--mono)">${r.symbol.replace('-USD','')}</span>
        <div><div class="vol-bar-track"><div class="vol-bar-fill ${risk}" style="width:${pct}%"></div></div><span style="font-size:11px;color:var(--text-3)">${pct}% of max</span></div>
        <span style="font-size:14px;font-weight:700;font-family:var(--mono)">${volPct(r.predicted_volatility)}</span>
        <span><span class="risk-chip ${risk}">${risk.toUpperCase()}</span></span>
        <span style="font-size:13px;color:var(--text-2)">${volPct(r.realized_volatility||0)}</span>
      </div>`;}).join('');
  }catch(e){err.style.display='flex';err.innerHTML=`<span class="material-symbols-outlined">error</span> ${e.message}`;}
  finally{ld.style.display='none';}
}

async function explorerPredict(){
  const out=document.getElementById('ex-out-predict');out.textContent='Loading…';
  try{const r=await fetch('/api/predict',{method:'POST',headers:{'Content-Type':'application/json'},
    body:JSON.stringify({symbol:document.getElementById('ex-symbol').value,period:document.getElementById('ex-period').value,horizon_days:parseInt(document.getElementById('ex-horizon').value)})});
    out.textContent=JSON.stringify(await r.json(),null,2);}catch(e){out.textContent=e.message;}
}

async function explorerBatch(){
  const out=document.getElementById('ex-out-batch');out.textContent='Loading…';
  const syms=document.getElementById('ex-batch-syms').value.split(',').map(s=>s.trim());
  try{const r=await fetch('/api/batch',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({symbols:syms,period:'2y',horizon_days:30})});
    out.textContent=JSON.stringify(await r.json(),null,2);}catch(e){out.textContent=e.message;}
}

async function explorerHealth(){
  const out=document.getElementById('ex-out-health');out.textContent='Loading…';
  try{const r=await fetch('/api/health');out.textContent=JSON.stringify(await r.json(),null,2);}catch(e){out.textContent=e.message;}
}

buildChips();
checkHealth();
setInterval(checkHealth,30000);
</script>
</body>
</html>"""

@app.route("/")
def index():
    return render_template_string(HTML)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
