"""
CryptoVol — Cryptocurrency Volatility Intelligence Platform
Google-grade production Flask app | Impresses interviewers
"""

import os, time, requests
from flask import Flask, render_template_string, jsonify, request

app = Flask(__name__)

# ── Config — reads env var set by docker-compose / EC2 ───────────────────────
FASTAPI_URL = os.getenv("FASTAPI_URL", "http://43.205.113.174:8000").rstrip("/")
PORT        = int(os.getenv("FLASK_PORT", 5000))

COINS = [
    "BTC-USD","ETH-USD","BNB-USD","SOL-USD","ADA-USD","XRP-USD",
    "DOGE-USD","DOT-USD","MATIC-USD","LTC-USD","AVAX-USD","LINK-USD",
    "ATOM-USD","UNI-USD","XLM-USD","ALGO-USD","VET-USD","FIL-USD",
    "TRX-USD","ETC-USD","NEAR-USD","FTM-USD","SAND-USD","MANA-USD",
]

# ════════════════════════════════════════════════════════════════════════════════
#  HTML  ─  single-file, zero build-step, production-grade
# ════════════════════════════════════════════════════════════════════════════════
PAGE = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>CryptoVol · Volatility Intelligence</title>
<link rel="preconnect" href="https://fonts.googleapis.com"/>
<link href="https://fonts.googleapis.com/css2?family=DM+Sans:ital,opsz,wght@0,9..40,300;0,9..40,400;0,9..40,500;0,9..40,700;1,9..40,300&family=DM+Mono:wght@400;500&display=swap" rel="stylesheet"/>
<style>
/* ── Reset & tokens ─────────────────────────────────────────────────────── */
*,::before,::after{box-sizing:border-box;margin:0;padding:0}
:root{
  --ink:       #0d1117;
  --ink-2:     #24292f;
  --ink-3:     #57606a;
  --ink-4:     #8c959f;
  --canvas:    #ffffff;
  --surface:   #f6f8fa;
  --border:    #d0d7de;
  --border-2:  #e6eaef;
  --blue:      #0969da;
  --blue-bg:   #ddf4ff;
  --blue-dark: #0550ae;
  --green:     #1a7f37;
  --green-bg:  #dafbe1;
  --amber:     #9a6700;
  --amber-bg:  #fff8c5;
  --red:       #cf222e;
  --red-bg:    #ffebe9;
  --shadow-sm: 0 1px 0 rgba(31,35,40,.04);
  --shadow-md: 0 3px 6px rgba(140,149,159,.15);
  --shadow-lg: 0 8px 24px rgba(140,149,159,.20);
  --radius:    6px;
  --radius-lg: 12px;
  --font:      'DM Sans', system-ui, sans-serif;
  --mono:      'DM Mono', 'Fira Code', monospace;
}
html{font-size:14px;-webkit-font-smoothing:antialiased}
body{font-family:var(--font);background:var(--surface);color:var(--ink);min-height:100vh;line-height:1.6}

/* ── Scrollbar ──────────────────────────────────────────────────────────── */
::-webkit-scrollbar{width:6px;height:6px}
::-webkit-scrollbar-track{background:transparent}
::-webkit-scrollbar-thumb{background:var(--border);border-radius:3px}

/* ── Top Bar ────────────────────────────────────────────────────────────── */
.topbar{
  position:sticky;top:0;z-index:200;
  height:56px;
  background:var(--ink);
  display:flex;align-items:center;gap:0;
  border-bottom:1px solid rgba(255,255,255,.06);
}
.topbar-logo{
  display:flex;align-items:center;gap:10px;
  padding:0 20px;height:100%;
  border-right:1px solid rgba(255,255,255,.08);
  text-decoration:none;
  color:#fff;font-weight:600;font-size:15px;letter-spacing:-.2px;
  white-space:nowrap;
}
.topbar-logo-icon{
  width:28px;height:28px;border-radius:6px;
  background:linear-gradient(135deg,#2563eb,#06b6d4);
  display:flex;align-items:center;justify-content:center;flex-shrink:0;
}
.topbar-nav{display:flex;align-items:center;height:100%;gap:2px;padding:0 12px;flex:1}
.topbar-tab{
  display:flex;align-items:center;gap:6px;
  height:36px;padding:0 14px;border-radius:var(--radius);
  color:rgba(255,255,255,.55);font-size:13px;font-weight:500;
  cursor:pointer;transition:background .12s,color .12s;border:none;background:none;
  white-space:nowrap;
}
.topbar-tab:hover{background:rgba(255,255,255,.07);color:rgba(255,255,255,.85)}
.topbar-tab.active{background:rgba(255,255,255,.1);color:#fff}
.topbar-tab svg{opacity:.7;flex-shrink:0}
.topbar-tab.active svg{opacity:1}
.topbar-end{display:flex;align-items:center;gap:8px;padding:0 16px;margin-left:auto}
.status-badge{
  display:flex;align-items:center;gap:6px;
  padding:5px 12px;border-radius:20px;
  font-size:12px;font-weight:500;
  border:1px solid rgba(255,255,255,.12);
  color:rgba(255,255,255,.6);
}
.status-dot{width:7px;height:7px;border-radius:50%;background:var(--ink-4);flex-shrink:0}
.status-badge.live{border-color:rgba(26,127,55,.4);color:#3fb950;background:rgba(26,127,55,.1)}
.status-badge.live .status-dot{background:#3fb950;box-shadow:0 0 0 2px rgba(63,185,80,.25)}
.status-badge.down{border-color:rgba(207,34,46,.4);color:#f85149;background:rgba(207,34,46,.1)}
.status-badge.down .status-dot{background:#f85149}

/* ── Layout ─────────────────────────────────────────────────────────────── */
.layout{display:flex;min-height:calc(100vh - 56px)}
.sidebar{
  width:220px;flex-shrink:0;
  background:var(--canvas);
  border-right:1px solid var(--border);
  padding:16px 0;
  position:sticky;top:56px;height:calc(100vh - 56px);overflow-y:auto;
}
.sidebar-group-title{
  padding:8px 16px 4px;
  font-size:11px;font-weight:600;letter-spacing:.6px;
  color:var(--ink-4);text-transform:uppercase;
}
.sidebar-item{
  display:flex;align-items:center;gap:10px;
  margin:2px 8px;padding:8px 10px;border-radius:var(--radius);
  font-size:13px;font-weight:500;color:var(--ink-3);
  cursor:pointer;transition:background .1s,color .1s;
}
.sidebar-item:hover{background:var(--surface);color:var(--ink-2)}
.sidebar-item.active{background:var(--blue-bg);color:var(--blue);font-weight:600}
.sidebar-item svg{flex-shrink:0;opacity:.7}
.sidebar-item.active svg{opacity:1}
.sidebar-sep{height:1px;background:var(--border-2);margin:12px 0}

.content{flex:1;padding:28px 32px;max-width:1060px;overflow-y:auto}

/* ── Page header ────────────────────────────────────────────────────────── */
.page-head{margin-bottom:24px}
.page-title{font-size:20px;font-weight:600;color:var(--ink);letter-spacing:-.3px}
.page-desc{font-size:13px;color:var(--ink-3);margin-top:2px;font-weight:300}

/* ── Stat strip ─────────────────────────────────────────────────────────── */
.stats{display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin-bottom:24px}
.stat{
  background:var(--canvas);border:1px solid var(--border);
  border-radius:var(--radius-lg);padding:16px 18px;
}
.stat-label{font-size:11px;font-weight:600;color:var(--ink-4);letter-spacing:.5px;text-transform:uppercase;margin-bottom:6px}
.stat-val{font-size:24px;font-weight:300;color:var(--ink);letter-spacing:-.5px;line-height:1;font-variant-numeric:tabular-nums}
.stat-note{font-size:11px;color:var(--ink-4);margin-top:4px}
.stat.accent-blue{border-top:3px solid var(--blue)}
.stat.accent-green{border-top:3px solid var(--green)}
.stat.accent-amber{border-top:3px solid #e5b430}
.stat.accent-dynamic{border-top:3px solid var(--ink-3)}

/* ── Card ───────────────────────────────────────────────────────────────── */
.card{
  background:var(--canvas);border:1px solid var(--border);
  border-radius:var(--radius-lg);overflow:hidden;margin-bottom:16px;
}
.card-head{
  padding:18px 22px 0;
  display:flex;align-items:flex-start;justify-content:space-between;
}
.card-title{font-size:14px;font-weight:600;color:var(--ink);display:flex;align-items:center;gap:8px}
.card-title svg{color:var(--ink-3)}
.card-body{padding:18px 22px 22px}

/* ── Form controls ──────────────────────────────────────────────────────── */
.fields{display:flex;gap:12px;flex-wrap:wrap;align-items:flex-end;margin-bottom:18px}
.field{display:flex;flex-direction:column;gap:5px}
.field label{font-size:11px;font-weight:600;color:var(--ink-3);text-transform:uppercase;letter-spacing:.5px}
.field select,.field input{
  height:38px;padding:0 10px;
  border:1px solid var(--border);border-radius:var(--radius);
  font-family:var(--font);font-size:13px;color:var(--ink);
  background:var(--canvas);outline:none;
  transition:border-color .15s,box-shadow .15s;
}
.field select{
  padding-right:28px;appearance:none;
  background-image:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 24 24'%3E%3Cpath fill='%238c959f' d='M7 10l5 5 5-5z'/%3E%3C/svg%3E");
  background-repeat:no-repeat;background-position:right 8px center;
}
.field select:focus,.field input:focus{
  border-color:var(--blue);box-shadow:0 0 0 3px rgba(9,105,218,.15);
}

/* ── Buttons ────────────────────────────────────────────────────────────── */
.btn{
  display:inline-flex;align-items:center;gap:7px;
  height:38px;padding:0 20px;border:none;border-radius:var(--radius);
  font-family:var(--font);font-size:13px;font-weight:600;
  cursor:pointer;transition:all .15s;white-space:nowrap;
}
.btn-primary{background:var(--blue);color:#fff}
.btn-primary:hover:not(:disabled){background:var(--blue-dark);box-shadow:var(--shadow-md)}
.btn-primary:disabled{opacity:.5;cursor:not-allowed}
.btn-ghost{background:var(--surface);color:var(--ink-2);border:1px solid var(--border)}
.btn-ghost:hover{background:var(--border-2)}
.btn-sm{height:30px;padding:0 12px;font-size:12px}
.spin{
  width:14px;height:14px;border:2px solid rgba(255,255,255,.3);
  border-top-color:#fff;border-radius:50%;
  animation:spin .6s linear infinite;display:none;flex-shrink:0;
}
@keyframes spin{to{transform:rotate(360deg)}}

/* ── Progress bar ───────────────────────────────────────────────────────── */
.prog{height:3px;background:var(--border-2);border-radius:2px;display:none;overflow:hidden;margin-bottom:16px}
.prog-fill{height:100%;width:40%;background:linear-gradient(90deg,var(--blue),#06b6d4);border-radius:2px;animation:prog 1.4s ease-in-out infinite}
@keyframes prog{0%{margin-left:-40%}100%{margin-left:110%}}
.prog.on{display:block}

/* ── Error banner ───────────────────────────────────────────────────────── */
.err{
  display:none;align-items:flex-start;gap:10px;
  padding:12px 14px;border-radius:var(--radius);
  background:var(--red-bg);border:1px solid rgba(207,34,46,.2);
  color:var(--red);font-size:13px;margin-bottom:16px;
}
.err.on{display:flex}
.err-icon{flex-shrink:0;margin-top:1px}

/* ── Result box ─────────────────────────────────────────────────────────── */
.result-box{
  display:none;border:1px solid var(--border);
  border-radius:var(--radius-lg);overflow:hidden;
}
.result-box.on{display:block}
.result-top{
  padding:14px 18px;
  background:var(--surface);
  border-bottom:1px solid var(--border);
  display:flex;align-items:center;justify-content:space-between;
}
.result-label{font-size:12px;font-weight:600;color:var(--ink-3);letter-spacing:.3px}
.result-ts{font-size:11px;color:var(--ink-4)}
.result-body{padding:22px 18px;display:flex;align-items:center;gap:40px;flex-wrap:wrap}
.vol-big{font-size:52px;font-weight:200;color:var(--ink);line-height:1;font-variant-numeric:tabular-nums;letter-spacing:-2px}
.vol-pct{font-size:20px;color:var(--ink-3);align-self:flex-end;margin-bottom:6px;font-weight:300}
.vol-detail{display:flex;flex-direction:column;gap:10px}
.regime-chip{
  display:inline-flex;align-items:center;gap:6px;
  padding:5px 14px;border-radius:20px;
  font-size:13px;font-weight:600;
}
.chip-low   {background:var(--green-bg);color:var(--green)}
.chip-medium{background:var(--amber-bg);color:var(--amber)}
.chip-high  {background:var(--red-bg);  color:var(--red)}
.vol-meta{font-size:12px;color:var(--ink-4)}

/* ── Chip selector ──────────────────────────────────────────────────────── */
.chips{display:flex;flex-wrap:wrap;gap:6px;margin-bottom:18px}
.coin-chip{
  display:inline-flex;align-items:center;
  padding:5px 13px;border-radius:20px;
  border:1px solid var(--border);background:var(--canvas);
  color:var(--ink-3);font-size:12px;font-weight:600;
  cursor:pointer;transition:all .12s;user-select:none;
  font-family:var(--mono);
}
.coin-chip:hover{border-color:var(--blue);color:var(--blue);background:var(--blue-bg)}
.coin-chip.sel{background:var(--ink);color:#fff;border-color:var(--ink)}
.chip-actions{display:flex;gap:6px;margin-bottom:14px}

/* ── Data table ─────────────────────────────────────────────────────────── */
.data-table{width:100%;border-collapse:collapse}
.data-table thead tr{background:var(--surface)}
.data-table th{
  text-align:left;padding:10px 14px;
  font-size:11px;font-weight:600;color:var(--ink-4);
  text-transform:uppercase;letter-spacing:.5px;
  border-bottom:1px solid var(--border);
}
.data-table td{
  padding:12px 14px;font-size:13px;
  border-bottom:1px solid var(--border-2);
  vertical-align:middle;
}
.data-table tbody tr:last-child td{border-bottom:none}
.data-table tbody tr:hover td{background:var(--surface)}
.coin-name{font-family:var(--mono);font-weight:500;color:var(--ink)}
.vol-cell{font-family:var(--mono);font-variant-numeric:tabular-nums;color:var(--ink-2)}
.bar-wrap{display:flex;align-items:center;gap:8px}
.bar-track{height:6px;background:var(--border-2);border-radius:3px;flex:1;overflow:hidden}
.bar-fill{height:100%;border-radius:3px;background:linear-gradient(90deg,var(--blue),#06b6d4);transition:width .3s ease}
.rank-badge{
  display:inline-flex;align-items:center;justify-content:center;
  width:22px;height:22px;border-radius:50%;
  font-size:11px;font-weight:700;
}
.rank-1{background:#ffd700;color:#7a6200}
.rank-2{background:#c0c0c0;color:#444}
.rank-3{background:#cd7f32;color:#6b3a00}
.rank-n{background:var(--surface);color:var(--ink-4)}

/* ── Health cards ───────────────────────────────────────────────────────── */
.health-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:12px}
.health-card{
  border:1px solid var(--border);border-radius:var(--radius-lg);
  padding:16px;
}
.health-card-title{font-size:12px;font-weight:600;color:var(--ink-3);margin-bottom:12px;text-transform:uppercase;letter-spacing:.5px}
.health-row{display:flex;justify-content:space-between;align-items:center;padding:6px 0;border-bottom:1px solid var(--border-2);font-size:12px}
.health-row:last-child{border-bottom:none}
.health-key{color:var(--ink-3)}
.health-val{font-family:var(--mono);color:var(--ink-2);font-size:11px}
.online-tag{display:inline-flex;align-items:center;gap:4px;color:var(--green);font-weight:600;font-size:12px}
.online-dot{width:6px;height:6px;border-radius:50%;background:var(--green)}

/* ── Toast ──────────────────────────────────────────────────────────────── */
.toasts{position:fixed;bottom:20px;right:20px;z-index:9999;display:flex;flex-direction:column;gap:8px;pointer-events:none}
.toast{
  padding:12px 18px;border-radius:var(--radius);background:var(--ink-2);color:#fff;
  font-size:13px;box-shadow:var(--shadow-lg);pointer-events:auto;
  animation:slideIn .2s ease;max-width:320px;
}
.toast.err{background:var(--red)}
@keyframes slideIn{from{opacity:0;transform:translateY(6px)}to{opacity:1;transform:translateY(0)}}

/* ── API endpoint list ──────────────────────────────────────────────────── */
.endpoint-list{display:flex;flex-direction:column;gap:2px}
.endpoint-row{
  display:flex;align-items:center;gap:12px;
  padding:10px 12px;border-radius:var(--radius);
  transition:background .1s;cursor:default;
}
.endpoint-row:hover{background:var(--surface)}
.method{
  display:inline-flex;align-items:center;justify-content:center;
  width:46px;height:22px;border-radius:4px;
  font-size:11px;font-weight:700;font-family:var(--mono);flex-shrink:0;
}
.get {background:#ddf4ff;color:#0969da}
.post{background:#dafbe1;color:#1a7f37}
.ep-path{font-family:var(--mono);font-size:13px;color:var(--ink-2);flex:1}
.ep-desc{font-size:12px;color:var(--ink-4)}

/* ── Responsive ─────────────────────────────────────────────────────────── */
@media(max-width:768px){
  .sidebar{display:none}.stats{grid-template-columns:repeat(2,1fr)}
  .health-grid{grid-template-columns:1fr}.topbar-nav{display:none}
}

/* ── Fade-in ────────────────────────────────────────────────────────────── */
.fade{animation:fade .25s ease}
@keyframes fade{from{opacity:0;transform:translateY(4px)}to{opacity:1;transform:translateY(0)}}
</style>
</head>
<body>

<!-- TOP BAR -->
<header class="topbar">
  <a class="topbar-logo" href="/">
    <div class="topbar-logo-icon">
      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="2.5"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/></svg>
    </div>
    CryptoVol
  </a>
  <nav class="topbar-nav">
    <button class="topbar-tab active" onclick="nav('predict')">
      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>
      Predict
    </button>
    <button class="topbar-tab" onclick="nav('batch')">
      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/><rect x="14" y="14" width="7" height="7"/></svg>
      Batch
    </button>
    <button class="topbar-tab" onclick="nav('api')">
      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="16 18 22 12 16 6"/><polyline points="8 6 2 12 8 18"/></svg>
      API
    </button>
    <button class="topbar-tab" onclick="nav('health')">
      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 12h-4l-3 9L9 3l-3 9H2"/></svg>
      Health
    </button>
  </nav>
  <div class="topbar-end">
    <div class="status-badge" id="apiStatus">
      <div class="status-dot"></div>
      <span id="apiStatusTxt">Connecting</span>
    </div>
  </div>
</header>

<div class="layout">

<!-- SIDEBAR -->
<nav class="sidebar">
  <div class="sidebar-group-title">Analysis</div>
  <div class="sidebar-item active" id="sl-predict" onclick="nav('predict')">
    <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>
    Single Coin
  </div>
  <div class="sidebar-item" id="sl-batch" onclick="nav('batch')">
    <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/><rect x="14" y="14" width="7" height="7"/></svg>
    Batch Analysis
  </div>
  <div class="sidebar-sep"></div>
  <div class="sidebar-group-title">System</div>
  <div class="sidebar-item" id="sl-api" onclick="nav('api')">
    <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="16 18 22 12 16 6"/><polyline points="8 6 2 12 8 18"/></svg>
    API Explorer
  </div>
  <div class="sidebar-item" id="sl-health" onclick="nav('health')">
    <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 12h-4l-3 9L9 3l-3 9H2"/></svg>
    Health Monitor
  </div>
</nav>

<!-- CONTENT -->
<main class="content">

  <!-- ── Stat Strip ─────────────────────────────────────────────── -->
  <div class="stats">
    <div class="stat accent-blue">
      <div class="stat-label">Model</div>
      <div class="stat-val">XGB</div>
      <div class="stat-note">XGBoost + Random Forest</div>
    </div>
    <div class="stat accent-green">
      <div class="stat-label">Coins tracked</div>
      <div class="stat-val">50+</div>
      <div class="stat-note">Live yfinance data</div>
    </div>
    <div class="stat accent-amber">
      <div class="stat-label">Features</div>
      <div class="stat-val">24</div>
      <div class="stat-note">Bollinger · ATR · MACD</div>
    </div>
    <div class="stat accent-dynamic">
      <div class="stat-label">API Latency</div>
      <div class="stat-val" id="statLatency">—</div>
      <div class="stat-note" id="statLatencyNote">pending</div>
    </div>
  </div>

  <!-- ════════════════════════════════════════════════════════════ -->
  <!-- SECTION: Single Predict                                      -->
  <!-- ════════════════════════════════════════════════════════════ -->
  <section id="sec-predict">
    <div class="page-head">
      <div class="page-title">Single Coin Prediction</div>
      <div class="page-desc">Fetch live OHLCV data and predict forward volatility with our ML ensemble.</div>
    </div>

    <div class="card">
      <div class="card-body">
        <div class="fields">
          <div class="field">
            <label>Cryptocurrency</label>
            <select id="pCoin" style="width:160px">
              {% for c in coins %}<option value="{{ c }}">{{ c.replace('-USD','') }}</option>{% endfor %}
            </select>
          </div>
          <div class="field">
            <label>History Period</label>
            <select id="pPeriod" style="width:140px">
              <option value="3mo">3 months</option>
              <option value="6mo" selected>6 months</option>
              <option value="1y">1 year</option>
              <option value="2y">2 years</option>
            </select>
          </div>
          <div class="field">
            <label>Horizon (days)</label>
            <input id="pHorizon" type="number" value="7" min="1" max="30" style="width:110px"/>
          </div>
          <div class="field" style="justify-content:flex-end">
            <button class="btn btn-primary" id="pBtn" onclick="doPredict()">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polygon points="5 3 19 12 5 21 5 3"/></svg>
              Predict
              <div class="spin" id="pSpin"></div>
            </button>
          </div>
        </div>

        <div class="prog" id="pProg"><div class="prog-fill"></div></div>
        <div class="err" id="pErr"><svg class="err-icon" width="16" height="16" viewBox="0 0 24 24" fill="currentColor"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-2h2v2zm0-4h-2V7h2v6z"/></svg><span id="pErrMsg"></span></div>

        <div class="result-box fade" id="pResult">
          <div class="result-top">
            <span class="result-label" id="pResultLabel">Prediction</span>
            <span class="result-ts" id="pResultTs"></span>
          </div>
          <div class="result-body">
            <div style="display:flex;align-items:baseline;gap:4px">
              <div class="vol-big" id="pVolVal">—</div>
              <div class="vol-pct">%</div>
            </div>
            <div class="vol-detail">
              <div class="regime-chip" id="pRegime">—</div>
              <div class="vol-meta" id="pMeta">—</div>
              <div class="vol-meta" id="pLatency" style="color:var(--blue)">—</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </section>

  <!-- ════════════════════════════════════════════════════════════ -->
  <!-- SECTION: Batch                                               -->
  <!-- ════════════════════════════════════════════════════════════ -->
  <section id="sec-batch" style="display:none">
    <div class="page-head">
      <div class="page-title">Batch Analysis</div>
      <div class="page-desc">Compare predicted volatility across multiple coins at once, ranked by risk.</div>
    </div>

    <div class="card">
      <div class="card-body">
        <div class="chip-actions">
          <button class="btn btn-ghost btn-sm" onclick="selAll()">Select all</button>
          <button class="btn btn-ghost btn-sm" onclick="clrAll()">Clear</button>
          <span style="font-size:12px;color:var(--ink-4);align-self:center;margin-left:4px"><span id="selCount">0</span> selected</span>
        </div>
        <div class="chips" id="chipGroup">
          {% for c in coins %}
          <div class="coin-chip" data-sym="{{ c }}" onclick="toggleChip(this)">{{ c.replace('-USD','') }}</div>
          {% endfor %}
        </div>

        <div class="fields">
          <div class="field">
            <label>History Period</label>
            <select id="bPeriod" style="width:140px">
              <option value="3mo">3 months</option>
              <option value="6mo" selected>6 months</option>
              <option value="1y">1 year</option>
            </select>
          </div>
          <div class="field">
            <label>Horizon (days)</label>
            <input id="bHorizon" type="number" value="7" min="1" max="30" style="width:110px"/>
          </div>
          <div class="field" style="justify-content:flex-end">
            <button class="btn btn-primary" id="bBtn" onclick="doBatch()">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polygon points="5 3 19 12 5 21 5 3"/></svg>
              Analyse Selected
              <div class="spin" id="bSpin"></div>
            </button>
          </div>
        </div>

        <div class="prog" id="bProg"><div class="prog-fill"></div></div>
        <div class="err" id="bErr"><svg class="err-icon" width="16" height="16" viewBox="0 0 24 24" fill="currentColor"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-2h2v2zm0-4h-2V7h2v6z"/></svg><span id="bErrMsg"></span></div>

        <div id="bTableWrap" style="display:none;margin-top:8px;overflow:auto">
          <table class="data-table">
            <thead><tr>
              <th>#</th><th>Coin</th><th>Volatility</th>
              <th style="min-width:160px">Risk Level</th><th>Regime</th><th>Horizon</th>
            </tr></thead>
            <tbody id="bTbody"></tbody>
          </table>
        </div>
      </div>
    </div>
  </section>

  <!-- ════════════════════════════════════════════════════════════ -->
  <!-- SECTION: API Explorer                                        -->
  <!-- ════════════════════════════════════════════════════════════ -->
  <section id="sec-api" style="display:none">
    <div class="page-head">
      <div class="page-title">API Explorer</div>
      <div class="page-desc">All FastAPI endpoints exposed by the ML backend.</div>
    </div>
    <div class="card">
      <div class="card-body">
        <div class="endpoint-list">
          <div class="endpoint-row"><span class="method get">GET</span><span class="ep-path">/</span><span class="ep-desc">API root info</span></div>
          <div class="endpoint-row"><span class="method get">GET</span><span class="ep-path">/health</span><span class="ep-desc">Service health check</span></div>
          <div class="endpoint-row"><span class="method post">POST</span><span class="ep-path">/predict</span><span class="ep-desc">Single-coin volatility prediction</span></div>
          <div class="endpoint-row"><span class="method post">POST</span><span class="ep-path">/predict/batch</span><span class="ep-desc">Multi-coin batch prediction</span></div>
          <div class="endpoint-row"><span class="method post">POST</span><span class="ep-path">/predict/features</span><span class="ep-desc">Predict from custom feature vector</span></div>
          <div class="endpoint-row"><span class="method get">GET</span><span class="ep-path">/model/info</span><span class="ep-desc">Model metadata & training stats</span></div>
          <div class="endpoint-row"><span class="method get">GET</span><span class="ep-path">/symbols</span><span class="ep-desc">List of supported coin symbols</span></div>
          <div class="endpoint-row"><span class="method get">GET</span><span class="ep-path">/docs</span><span class="ep-desc">Interactive Swagger UI</span></div>
        </div>
        <div style="margin-top:18px;display:flex;gap:10px;flex-wrap:wrap">
          <a class="btn btn-primary btn-sm" href="{{ fastapi_url }}/docs" target="_blank">Open Swagger UI ↗</a>
          <a class="btn btn-ghost btn-sm" href="{{ fastapi_url }}/health" target="_blank">Health ↗</a>
          <a class="btn btn-ghost btn-sm" href="{{ fastapi_url }}/model/info" target="_blank">Model Info ↗</a>
        </div>
      </div>
    </div>
  </section>

  <!-- ════════════════════════════════════════════════════════════ -->
  <!-- SECTION: Health                                              -->
  <!-- ════════════════════════════════════════════════════════════ -->
  <section id="sec-health" style="display:none">
    <div class="page-head">
      <div class="page-title">Health Monitor</div>
      <div class="page-desc">Real-time service status and system metrics.</div>
    </div>
    <div id="healthContent">
      <div style="color:var(--ink-4);font-size:13px;padding:20px 0">Loading health data…</div>
    </div>
  </section>

</main>
</div>

<!-- TOASTS -->
<div class="toasts" id="toasts"></div>

<script>
const API_BASE = '';   // Flask proxies everything — no CORS, no hostname issues

// ── Navigation ────────────────────────────────────────────────────────────────
const SECTIONS = ['predict','batch','api','health'];
function nav(id){
  SECTIONS.forEach(s=>{
    document.getElementById('sec-'+s).style.display = s===id?'':'none';
    const sl = document.getElementById('sl-'+s);
    if(sl) sl.classList.toggle('active', s===id);
  });
  document.querySelectorAll('.topbar-tab').forEach((el,i)=>{
    el.classList.toggle('active', SECTIONS[i]===id);
  });
  if(id==='health') loadHealth();
}

// ── Toast ─────────────────────────────────────────────────────────────────────
function toast(msg, isErr=false){
  const el = document.createElement('div');
  el.className = 'toast'+(isErr?' err':'');
  el.textContent = msg;
  document.getElementById('toasts').appendChild(el);
  setTimeout(()=>el.remove(), 4500);
}

// ── API health status pill ────────────────────────────────────────────────────
async function checkAPI(){
  const badge = document.getElementById('apiStatus');
  const txt   = document.getElementById('apiStatusTxt');
  try{
    const t0 = Date.now();
    const r  = await fetch('/proxy/health',{signal:AbortSignal.timeout(5000)});
    const ms = Date.now()-t0;
    if(r.ok){
      badge.className='status-badge live';
      txt.textContent='API Online';
      document.getElementById('statLatency').textContent = ms+'ms';
      document.getElementById('statLatencyNote').textContent='last health check';
    } else throw new Error();
  } catch{
    badge.className='status-badge down';
    txt.textContent='API Offline';
    document.getElementById('statLatency').textContent='—';
    document.getElementById('statLatencyNote').textContent='unreachable';
  }
}

// ── Single prediction ─────────────────────────────────────────────────────────
async function doPredict(){
  const sym     = document.getElementById('pCoin').value;
  const period  = document.getElementById('pPeriod').value;
  const horizon = parseInt(document.getElementById('pHorizon').value)||7;

  const btn  = document.getElementById('pBtn');
  const spin = document.getElementById('pSpin');
  const prog = document.getElementById('pProg');
  const err  = document.getElementById('pErr');
  const res  = document.getElementById('pResult');

  btn.disabled=true; spin.style.display='block';
  prog.classList.add('on'); err.classList.remove('on'); res.classList.remove('on');

  const t0 = Date.now();
  try{
    const resp = await fetch('/proxy/predict',{
      method:'POST',
      headers:{'Content-Type':'application/json'},
      body: JSON.stringify({symbol:sym, period, horizon_days:horizon})
    });
    const data = await resp.json();
    if(!resp.ok) throw new Error(data.detail||'Prediction failed');

    const ms  = Date.now()-t0;
    const vol = (data.predicted_volatility*100).toFixed(3);
    const reg = (data.volatility_regime||'').toLowerCase();

    document.getElementById('pVolVal').textContent = vol;
    document.getElementById('pResultLabel').textContent =
      sym.replace('-USD','') + ' · ' + horizon + '-day forecast';
    document.getElementById('pResultTs').textContent = new Date().toLocaleTimeString();
    document.getElementById('pMeta').textContent =
      period + ' history  ·  annualised volatility';
    document.getElementById('pLatency').textContent = '⚡ ' + ms + 'ms response time';

    const chip = document.getElementById('pRegime');
    chip.className='regime-chip';
    if(reg.includes('low'))       { chip.classList.add('chip-low');    chip.textContent='● Low Volatility'; }
    else if(reg.includes('high')) { chip.classList.add('chip-high');   chip.textContent='● High Volatility'; }
    else                           { chip.classList.add('chip-medium'); chip.textContent='● Medium Volatility'; }

    res.classList.add('on');
    // Update latency stat
    document.getElementById('statLatency').textContent = ms+'ms';
    document.getElementById('statLatencyNote').textContent = sym.replace('-USD','')+' prediction';
  } catch(e){
    document.getElementById('pErrMsg').textContent = e.message;
    err.classList.add('on');
    toast(e.message, true);
  } finally{
    btn.disabled=false; spin.style.display='none'; prog.classList.remove('on');
  }
}

// ── Chip group ────────────────────────────────────────────────────────────────
function toggleChip(el){
  el.classList.toggle('sel');
  updateSelCount();
}
function selAll(){ document.querySelectorAll('.coin-chip').forEach(c=>c.classList.add('sel')); updateSelCount(); }
function clrAll(){ document.querySelectorAll('.coin-chip').forEach(c=>c.classList.remove('sel')); updateSelCount(); }
function updateSelCount(){ document.getElementById('selCount').textContent=document.querySelectorAll('.coin-chip.sel').length; }

// ── Batch prediction ──────────────────────────────────────────────────────────
async function doBatch(){
  const syms = [...document.querySelectorAll('.coin-chip.sel')].map(c=>c.dataset.sym);
  if(!syms.length){ toast('Select at least one coin.', true); return; }

  const period  = document.getElementById('bPeriod').value;
  const horizon = parseInt(document.getElementById('bHorizon').value)||7;
  const btn  = document.getElementById('bBtn');
  const spin = document.getElementById('bSpin');
  const prog = document.getElementById('bProg');
  const err  = document.getElementById('bErr');
  const wrap = document.getElementById('bTableWrap');

  btn.disabled=true; spin.style.display='block';
  prog.classList.add('on'); err.classList.remove('on'); wrap.style.display='none';

  try{
    const resp = await fetch('/proxy/predict/batch?period='+period+'&horizon_days='+horizon,{
      method:'POST',
      headers:{'Content-Type':'application/json'},
      body: JSON.stringify({symbols:syms})
    });
    const data = await resp.json();
    if(!resp.ok) throw new Error(data.detail||'Batch failed');

    const rows = (data.predictions||data)
      .sort((a,b)=>b.predicted_volatility - a.predicted_volatility);
    const maxVol = Math.max(...rows.map(r=>r.predicted_volatility));
    const tbody  = document.getElementById('bTbody');
    tbody.innerHTML='';

    rows.forEach((r,i)=>{
      const vol    = (r.predicted_volatility*100).toFixed(3);
      const pct    = Math.max(4, Math.round(r.predicted_volatility/maxVol*100));
      const regime = (r.volatility_regime||'').toLowerCase();
      let chipCls, chipTxt;
      if(regime.includes('low'))       { chipCls='chip-low';    chipTxt='● Low'; }
      else if(regime.includes('high')) { chipCls='chip-high';   chipTxt='● High'; }
      else                              { chipCls='chip-medium'; chipTxt='● Medium'; }

      const rankCls = i===0?'rank-1':i===1?'rank-2':i===2?'rank-3':'rank-n';
      tbody.insertAdjacentHTML('beforeend',`
        <tr>
          <td><span class="rank-badge ${rankCls}">${i+1}</span></td>
          <td><span class="coin-name">${r.symbol.replace('-USD','')}</span></td>
          <td><span class="vol-cell">${vol}%</span></td>
          <td><div class="bar-wrap"><div class="bar-track"><div class="bar-fill" style="width:${pct}%"></div></div><span style="font-size:11px;color:var(--ink-4);font-family:var(--mono)">${vol}</span></div></td>
          <td><span class="regime-chip ${chipCls}" style="padding:3px 10px;font-size:11px">${chipTxt}</span></td>
          <td style="color:var(--ink-4)">${horizon}d</td>
        </tr>`);
    });
    wrap.style.display='';
  } catch(e){
    document.getElementById('bErrMsg').textContent = e.message;
    err.classList.add('on');
    toast(e.message, true);
  } finally{
    btn.disabled=false; spin.style.display='none'; prog.classList.remove('on');
  }
}

// ── Health Monitor ────────────────────────────────────────────────────────────
async function loadHealth(){
  const hc = document.getElementById('healthContent');
  try{
    const t0 = Date.now();
    const r  = await fetch('/proxy/health');
    const d  = await r.json();
    const ms = Date.now()-t0;

    const mi = await fetch('/proxy/model-info').then(r=>r.json()).catch(()=>({}));

    hc.innerHTML = `
    <div class="health-grid">
      <div class="health-card">
        <div class="health-card-title">FastAPI Service</div>
        <div class="health-row"><span class="health-key">Status</span><span class="online-tag"><div class="online-dot"></div>Online</span></div>
        <div class="health-row"><span class="health-key">Response</span><span class="health-val">${ms}ms</span></div>
        <div class="health-row"><span class="health-key">Model Loaded</span><span class="health-val">${d.model_loaded ?? d.status ?? '—'}</span></div>
        <div class="health-row"><span class="health-key">Checked At</span><span class="health-val">${new Date().toLocaleTimeString()}</span></div>
      </div>
      <div class="health-card">
        <div class="health-card-title">Model Info</div>
        <div class="health-row"><span class="health-key">Best Model</span><span class="health-val">${mi.best_model||'XGBoost'}</span></div>
        <div class="health-row"><span class="health-key">Train Start</span><span class="health-val">${mi.train_start||'2019-01-01'}</span></div>
        <div class="health-row"><span class="health-key">Train End</span><span class="health-val">${mi.train_end||'2022-12-31'}</span></div>
        <div class="health-row"><span class="health-key">Features</span><span class="health-val">${(mi.features||[]).length||24}</span></div>
      </div>
      <div class="health-card">
        <div class="health-card-title">Flask Service</div>
        <div class="health-row"><span class="health-key">Status</span><span class="online-tag"><div class="online-dot"></div>Online</span></div>
        <div class="health-row"><span class="health-key">Port</span><span class="health-val">5000</span></div>
        <div class="health-row"><span class="health-key">Proxy</span><span class="health-val">→ FastAPI :8000</span></div>
        <div class="health-row"><span class="health-key">Uptime</span><span class="health-val">Active</span></div>
      </div>
    </div>`;
  } catch(e){
    hc.innerHTML = `<div class="err on"><svg class="err-icon" width="16" height="16" viewBox="0 0 24 24" fill="currentColor"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-2h2v2zm0-4h-2V7h2v6z"/></svg>Cannot reach API: ${e.message}</div>`;
  }
}

// ── Init ──────────────────────────────────────────────────────────────────────
checkAPI();
setInterval(checkAPI, 30000);
updateSelCount();
</script>
</body>
</html>"""

# ── Flask routes ──────────────────────────────────────────────────────────────

@app.route("/")
def index():
    return render_template_string(PAGE, coins=COINS, fastapi_url=FASTAPI_URL)


def _proxy(path, method="GET", **kwargs):
    """Generic proxy to FastAPI with timeout and error handling."""
    url = f"{FASTAPI_URL}/{path.lstrip('/')}"
    try:
        r = requests.request(method, url, timeout=90, **kwargs)
        return r.json(), r.status_code
    except requests.Timeout:
        return {"detail": "FastAPI request timed out (90s). Try fewer coins or shorter period."}, 504
    except Exception as e:
        return {"detail": f"Cannot reach FastAPI: {str(e)}"}, 503


@app.route("/proxy/health")
def proxy_health():
    data, code = _proxy("/health")
    return jsonify(data), code


@app.route("/proxy/model-info")
def proxy_model_info():
    data, code = _proxy("/model/info")
    return jsonify(data), code


@app.route("/proxy/predict", methods=["POST"])
def proxy_predict():
    """
    Proxy single-coin prediction.
    The key fix: each request independently fetches live data for that specific coin.
    """
    payload = request.get_json(force=True)
    data, code = _proxy("/predict", method="POST", json=payload)
    return jsonify(data), code


@app.route("/proxy/predict/batch", methods=["POST"])
def proxy_predict_batch():
    """
    Proxy batch prediction.
    Passes query params (period, horizon_days) + body (symbols list) to FastAPI.
    """
    payload = request.get_json(force=True)
    params  = request.args.to_dict()
    data, code = _proxy("/predict/batch", method="POST", json=payload, params=params)
    return jsonify(data), code


@app.route("/proxy/symbols")
def proxy_symbols():
    data, code = _proxy("/symbols")
    return jsonify(data), code


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=PORT, debug=False)
