"""
CryptoVol – Cryptocurrency Volatility Prediction Dashboard
Production Flask Application  |  Google-grade UI
"""

import os
import requests
from flask import Flask, render_template_string, jsonify, request

app = Flask(__name__)

# ── Configuration ────────────────────────────────────────────────────────────
FASTAPI_URL = os.getenv("FASTAPI_URL", "http://43.205.113.174:8000")
PORT        = int(os.getenv("FLASK_PORT", 5000))

SUPPORTED_SYMBOLS = [
    "BTC-USD", "ETH-USD", "BNB-USD", "ADA-USD", "XRP-USD",
    "SOL-USD", "DOGE-USD", "DOT-USD", "MATIC-USD", "LTC-USD",
    "AVAX-USD", "LINK-USD", "ATOM-USD", "UNI-USD", "XLM-USD",
    "ALGO-USD", "VET-USD", "FIL-USD", "TRX-USD", "ETC-USD",
]

# ── HTML Template ─────────────────────────────────────────────────────────────
HTML = r"""
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>CryptoVol · Volatility Intelligence</title>
  <link rel="preconnect" href="https://fonts.googleapis.com"/>
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin/>
  <link href="https://fonts.googleapis.com/css2?family=Google+Sans:wght@400;500;700&family=Google+Sans+Mono&family=Roboto:wght@300;400;500&display=swap" rel="stylesheet"/>
  <style>
    /* ── Design Tokens ─────────────────────────────────── */
    :root {
      --bg:           #f8f9fa;
      --surface:      #ffffff;
      --surface-2:    #f1f3f4;
      --border:       #dadce0;
      --text-primary: #202124;
      --text-secondary:#5f6368;
      --text-hint:    #80868b;
      --blue:         #1a73e8;
      --blue-hover:   #1557b0;
      --blue-light:   #e8f0fe;
      --green:        #1e8e3e;
      --green-light:  #e6f4ea;
      --yellow:       #f9ab00;
      --yellow-light: #fef7e0;
      --red:          #d93025;
      --red-light:    #fce8e6;
      --shadow-1:     0 1px 2px rgba(60,64,67,.3),0 1px 3px 1px rgba(60,64,67,.15);
      --shadow-2:     0 1px 3px rgba(60,64,67,.3),0 4px 8px 3px rgba(60,64,67,.15);
      --shadow-3:     0 2px 6px rgba(60,64,67,.3),0 6px 12px 4px rgba(60,64,67,.15);
      --radius:       8px;
      --radius-lg:    16px;
      --font:         'Google Sans', 'Roboto', sans-serif;
      --font-mono:    'Google Sans Mono', 'Roboto Mono', monospace;
    }

    *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

    body {
      font-family: var(--font);
      background: var(--bg);
      color: var(--text-primary);
      min-height: 100vh;
      font-size: 14px;
      line-height: 1.5;
    }

    /* ── App Shell ─────────────────────────────────────── */
    .app-bar {
      position: sticky; top: 0; z-index: 100;
      background: var(--surface);
      border-bottom: 1px solid var(--border);
      padding: 0 24px;
      height: 64px;
      display: flex; align-items: center; gap: 16px;
    }
    .app-bar-logo {
      display: flex; align-items: center; gap: 10px;
      font-size: 18px; font-weight: 500; color: var(--text-primary);
      text-decoration: none;
    }
    .app-bar-logo svg { flex-shrink: 0; }
    .app-bar-divider { color: var(--border); font-size: 22px; font-weight: 200; }
    .app-bar-subtitle { font-size: 13px; color: var(--text-secondary); font-weight: 400; }
    .app-bar-spacer { flex: 1; }
    .status-pill {
      display: flex; align-items: center; gap: 6px;
      padding: 6px 12px; border-radius: 20px;
      font-size: 12px; font-weight: 500;
      border: 1px solid var(--border);
    }
    .status-dot {
      width: 8px; height: 8px; border-radius: 50%;
      background: var(--text-hint);
    }
    .status-pill.online .status-dot { background: var(--green); }
    .status-pill.online { border-color: var(--green); color: var(--green); background: var(--green-light); }
    .status-pill.offline .status-dot { background: var(--red); }
    .status-pill.offline { border-color: var(--red); color: var(--red); background: var(--red-light); }

    /* ── Layout ────────────────────────────────────────── */
    .layout {
      display: grid;
      grid-template-columns: 240px 1fr;
      min-height: calc(100vh - 64px);
    }
    .sidebar {
      border-right: 1px solid var(--border);
      background: var(--surface);
      padding: 16px 0;
      position: sticky; top: 64px; height: calc(100vh - 64px); overflow-y: auto;
    }
    .nav-section-title {
      padding: 8px 16px 4px;
      font-size: 11px; font-weight: 500;
      color: var(--text-hint);
      letter-spacing: .8px; text-transform: uppercase;
    }
    .nav-item {
      display: flex; align-items: center; gap: 12px;
      padding: 10px 16px; cursor: pointer;
      font-size: 14px; color: var(--text-secondary);
      border-radius: 0 20px 20px 0; margin-right: 12px;
      transition: background .15s, color .15s;
    }
    .nav-item:hover { background: var(--surface-2); color: var(--text-primary); }
    .nav-item.active {
      background: var(--blue-light); color: var(--blue); font-weight: 500;
    }
    .nav-item svg { flex-shrink: 0; }

    /* ── Main Content ──────────────────────────────────── */
    .main { padding: 24px; max-width: 1100px; }

    /* ── Page Header ───────────────────────────────────── */
    .page-header { margin-bottom: 24px; }
    .page-title { font-size: 22px; font-weight: 400; color: var(--text-primary); }
    .page-subtitle { font-size: 14px; color: var(--text-secondary); margin-top: 2px; }

    /* ── Cards ─────────────────────────────────────────── */
    .card {
      background: var(--surface);
      border-radius: var(--radius-lg);
      border: 1px solid var(--border);
      margin-bottom: 16px;
      overflow: hidden;
    }
    .card-header {
      padding: 20px 24px 0;
      display: flex; align-items: center; justify-content: space-between;
    }
    .card-title {
      font-size: 16px; font-weight: 500; color: var(--text-primary);
      display: flex; align-items: center; gap: 8px;
    }
    .card-body { padding: 20px 24px 24px; }

    /* ── Metric Row ────────────────────────────────────── */
    .metric-grid {
      display: grid;
      grid-template-columns: repeat(4, 1fr);
      gap: 12px; margin-bottom: 24px;
    }
    .metric-card {
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: var(--radius-lg);
      padding: 20px;
    }
    .metric-label { font-size: 12px; color: var(--text-secondary); font-weight: 500; margin-bottom: 8px; }
    .metric-value { font-size: 28px; font-weight: 400; color: var(--text-primary); line-height: 1; }
    .metric-sub { font-size: 12px; color: var(--text-hint); margin-top: 4px; }
    .metric-card.blue { border-left: 3px solid var(--blue); }
    .metric-card.green { border-left: 3px solid var(--green); }
    .metric-card.yellow { border-left: 3px solid var(--yellow); }
    .metric-card.red { border-left: 3px solid var(--red); }

    /* ── Form Controls ─────────────────────────────────── */
    .form-row { display: flex; gap: 16px; flex-wrap: wrap; align-items: flex-end; margin-bottom: 20px; }
    .form-group { display: flex; flex-direction: column; gap: 6px; min-width: 180px; }
    .form-label { font-size: 12px; font-weight: 500; color: var(--text-secondary); }
    .form-select, .form-input {
      height: 40px; padding: 0 12px;
      border: 1px solid var(--border);
      border-radius: var(--radius);
      font-family: var(--font); font-size: 14px; color: var(--text-primary);
      background: var(--surface);
      outline: none; appearance: none;
      transition: border-color .15s, box-shadow .15s;
    }
    .form-select { background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='16' height='16' viewBox='0 0 24 24'%3E%3Cpath fill='%235f6368' d='M7 10l5 5 5-5z'/%3E%3C/svg%3E"); background-repeat: no-repeat; background-position: right 8px center; padding-right: 32px; }
    .form-select:focus, .form-input:focus { border-color: var(--blue); box-shadow: 0 0 0 2px rgba(26,115,232,.2); }

    /* ── Buttons ───────────────────────────────────────── */
    .btn {
      display: inline-flex; align-items: center; gap: 8px;
      height: 40px; padding: 0 24px;
      border: none; border-radius: 20px; cursor: pointer;
      font-family: var(--font); font-size: 14px; font-weight: 500;
      transition: box-shadow .15s, background .15s; white-space: nowrap;
    }
    .btn-primary { background: var(--blue); color: #fff; }
    .btn-primary:hover { background: var(--blue-hover); box-shadow: var(--shadow-1); }
    .btn-primary:disabled { background: var(--border); color: var(--text-hint); cursor: not-allowed; box-shadow: none; }
    .btn-outlined {
      background: transparent; color: var(--blue);
      border: 1px solid var(--blue);
    }
    .btn-outlined:hover { background: var(--blue-light); }

    /* ── Loading Spinner ───────────────────────────────── */
    .spinner {
      width: 20px; height: 20px; border: 2px solid rgba(255,255,255,.3);
      border-top-color: #fff; border-radius: 50%;
      animation: spin .7s linear infinite; display: none;
    }
    @keyframes spin { to { transform: rotate(360deg); } }

    /* ── Result Panel ──────────────────────────────────── */
    .result-panel {
      display: none;
      border: 1px solid var(--border);
      border-radius: var(--radius-lg);
      overflow: hidden; margin-top: 20px;
    }
    .result-panel.visible { display: block; }
    .result-header {
      padding: 16px 20px;
      background: var(--surface-2);
      border-bottom: 1px solid var(--border);
      display: flex; align-items: center; justify-content: space-between;
    }
    .result-title { font-size: 14px; font-weight: 500; }
    .result-body { padding: 20px; }

    /* ── Volatility Display ────────────────────────────── */
    .vol-display {
      display: flex; align-items: center; gap: 32px; flex-wrap: wrap;
    }
    .vol-number { font-size: 48px; font-weight: 300; line-height: 1; font-variant-numeric: tabular-nums; }
    .vol-unit { font-size: 18px; color: var(--text-secondary); align-self: flex-end; margin-bottom: 8px; }
    .vol-meta { display: flex; flex-direction: column; gap: 8px; }
    .vol-badge {
      display: inline-flex; align-items: center; gap: 6px;
      padding: 6px 14px; border-radius: 20px;
      font-size: 13px; font-weight: 500;
    }
    .badge-low    { background: var(--green-light);  color: var(--green); }
    .badge-medium { background: var(--yellow-light); color: #c77400; }
    .badge-high   { background: var(--red-light);    color: var(--red); }
    .vol-coin { font-size: 14px; color: var(--text-secondary); }
    .vol-latency { font-size: 12px; color: var(--text-hint); }

    /* ── Chip Group (coin selector) ────────────────────── */
    .chip-group { display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 20px; }
    .chip {
      display: inline-flex; align-items: center; gap: 4px;
      padding: 6px 14px; border-radius: 20px;
      border: 1px solid var(--border);
      background: var(--surface); color: var(--text-primary);
      font-size: 13px; font-weight: 500; cursor: pointer;
      transition: all .15s; user-select: none;
    }
    .chip:hover { background: var(--surface-2); border-color: #bdc1c6; }
    .chip.selected {
      background: var(--blue-light); color: var(--blue);
      border-color: var(--blue);
    }

    /* ── Batch Results Table ───────────────────────────── */
    .results-table { width: 100%; border-collapse: collapse; }
    .results-table th {
      text-align: left; padding: 10px 16px;
      font-size: 12px; font-weight: 500; color: var(--text-secondary);
      border-bottom: 1px solid var(--border);
      background: var(--surface-2);
    }
    .results-table td {
      padding: 12px 16px; font-size: 14px;
      border-bottom: 1px solid var(--border);
      vertical-align: middle;
    }
    .results-table tr:last-child td { border-bottom: none; }
    .results-table tr:hover td { background: var(--surface-2); }
    .vol-bar-wrap { display: flex; align-items: center; gap: 8px; }
    .vol-bar {
      height: 4px; border-radius: 2px;
      background: var(--blue); flex-shrink: 0;
      min-width: 4px;
    }

    /* ── Toast ─────────────────────────────────────────── */
    .toast-container {
      position: fixed; bottom: 24px; left: 50%;
      transform: translateX(-50%); z-index: 1000;
      display: flex; flex-direction: column; gap: 8px; pointer-events: none;
    }
    .toast {
      padding: 12px 20px; border-radius: var(--radius);
      background: #3c4043; color: #fff;
      font-size: 14px; box-shadow: var(--shadow-2);
      animation: slideUp .2s ease; pointer-events: auto;
    }
    .toast.error { background: var(--red); }
    @keyframes slideUp { from { opacity:0; transform:translateY(8px); } to { opacity:1; transform:translateY(0); } }

    /* ── Empty State ───────────────────────────────────── */
    .empty-state {
      text-align: center; padding: 48px 20px; color: var(--text-hint);
    }
    .empty-state svg { opacity: .4; margin-bottom: 12px; }
    .empty-state p { font-size: 14px; }

    /* ── Error Banner ──────────────────────────────────── */
    .error-banner {
      display: flex; align-items: center; gap: 10px;
      padding: 12px 16px; border-radius: var(--radius);
      background: var(--red-light); color: var(--red);
      font-size: 13px; margin-top: 12px; display: none;
    }
    .error-banner.visible { display: flex; }

    /* ── Progress Bar ──────────────────────────────────── */
    .progress-bar {
      height: 4px; background: var(--border); border-radius: 2px;
      overflow: hidden; margin-bottom: 20px; display: none;
    }
    .progress-fill {
      height: 100%; background: var(--blue);
      border-radius: 2px; animation: progress 1.5s ease-in-out infinite;
      width: 30%;
    }
    @keyframes progress {
      0%  { margin-left: -30%; width: 30%; }
      50% { width: 50%; }
      100%{ margin-left: 100%; width: 30%; }
    }
    .progress-bar.active { display: block; }

    /* ── Divider ───────────────────────────────────────── */
    .divider { height: 1px; background: var(--border); margin: 0 -24px; }

    /* ── API Info ──────────────────────────────────────── */
    .info-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 16px; }
    .info-row { display: flex; justify-content: space-between; padding: 8px 0; border-bottom: 1px solid var(--border); font-size: 13px; }
    .info-row:last-child { border-bottom: none; }
    .info-key { color: var(--text-secondary); }
    .info-val { font-family: var(--font-mono); color: var(--text-primary); }

    @media (max-width: 768px) {
      .layout { grid-template-columns: 1fr; }
      .sidebar { display: none; }
      .metric-grid { grid-template-columns: repeat(2, 1fr); }
      .info-grid { grid-template-columns: 1fr; }
    }
  </style>
</head>
<body>

<!-- App Bar -->
<header class="app-bar">
  <a class="app-bar-logo" href="/">
    <svg width="32" height="32" viewBox="0 0 32 32">
      <circle cx="16" cy="16" r="16" fill="#1a73e8"/>
      <path d="M10 22 L16 10 L22 22" stroke="#fff" stroke-width="2" fill="none" stroke-linecap="round" stroke-linejoin="round"/>
      <path d="M12 18h8" stroke="#fff" stroke-width="2" stroke-linecap="round"/>
      <circle cx="16" cy="10" r="2" fill="#fbbc04"/>
    </svg>
    CryptoVol
  </a>
  <span class="app-bar-divider">/</span>
  <span class="app-bar-subtitle">Volatility Intelligence Platform</span>
  <div class="app-bar-spacer"></div>
  <div class="status-pill" id="statusPill">
    <div class="status-dot"></div>
    <span id="statusText">Checking…</span>
  </div>
</header>

<!-- Layout -->
<div class="layout">

  <!-- Sidebar -->
  <nav class="sidebar">
    <div class="nav-section-title">Predict</div>
    <div class="nav-item active" onclick="showSection('single')">
      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>
      Single Coin
    </div>
    <div class="nav-item" onclick="showSection('batch')">
      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/><rect x="14" y="14" width="7" height="7"/></svg>
      Batch Analysis
    </div>
    <div style="height:16px"></div>
    <div class="nav-section-title">System</div>
    <div class="nav-item" onclick="showSection('api')">
      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="16 18 22 12 16 6"/><polyline points="8 6 2 12 8 18"/></svg>
      API Explorer
    </div>
    <div class="nav-item" onclick="showSection('health')">
      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 12h-4l-3 9L9 3l-3 9H2"/></svg>
      Health Monitor
    </div>
  </nav>

  <!-- Main -->
  <main class="main">

    <!-- Metric Strip -->
    <div class="metric-grid">
      <div class="metric-card blue">
        <div class="metric-label">SUPPORTED COINS</div>
        <div class="metric-value">50+</div>
        <div class="metric-sub">cryptocurrencies tracked</div>
      </div>
      <div class="metric-card green">
        <div class="metric-label">MODEL TYPE</div>
        <div class="metric-value">XGB</div>
        <div class="metric-sub">XGBoost + Random Forest ensemble</div>
      </div>
      <div class="metric-card yellow">
        <div class="metric-label">FEATURES</div>
        <div class="metric-value">24</div>
        <div class="metric-sub">engineered signals</div>
      </div>
      <div class="metric-card red" id="apiMetric">
        <div class="metric-label">API STATUS</div>
        <div class="metric-value" id="metricStatus">—</div>
        <div class="metric-sub" id="metricSub">connecting…</div>
      </div>
    </div>

    <!-- SECTION: Single Coin ─────────────────────────── -->
    <section id="section-single">
      <div class="page-header">
        <div class="page-title">Single Coin Prediction</div>
        <div class="page-subtitle">Select a cryptocurrency and forecast its volatility over a given horizon.</div>
      </div>

      <div class="card">
        <div class="card-body">
          <div class="form-row">
            <div class="form-group">
              <label class="form-label">CRYPTOCURRENCY</label>
              <select class="form-select" id="singleSymbol">
                {% for s in symbols %}
                <option value="{{ s }}">{{ s.replace('-USD','') }}</option>
                {% endfor %}
              </select>
            </div>
            <div class="form-group">
              <label class="form-label">HISTORY PERIOD</label>
              <select class="form-select" id="singlePeriod">
                <option value="3mo">3 Months</option>
                <option value="6mo" selected>6 Months</option>
                <option value="1y">1 Year</option>
                <option value="2y">2 Years</option>
              </select>
            </div>
            <div class="form-group">
              <label class="form-label">FORECAST HORIZON (days)</label>
              <input class="form-input" type="number" id="singleHorizon" value="7" min="1" max="30" style="width:140px"/>
            </div>
            <button class="btn btn-primary" id="singleBtn" onclick="predictSingle()">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polygon points="5 3 19 12 5 21 5 3"/></svg>
              Predict
              <div class="spinner" id="singleSpinner"></div>
            </button>
          </div>

          <div class="progress-bar" id="singleProgress"><div class="progress-fill"></div></div>

          <div class="error-banner" id="singleError">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-2h2v2zm0-4h-2V7h2v6z"/></svg>
            <span id="singleErrorMsg"></span>
          </div>

          <div class="result-panel" id="singleResult">
            <div class="result-header">
              <div class="result-title" id="singleResultTitle">Prediction Result</div>
              <span id="singleTimestamp" style="font-size:12px;color:var(--text-hint)"></span>
            </div>
            <div class="result-body">
              <div class="vol-display">
                <div>
                  <div style="font-size:12px;color:var(--text-secondary);font-weight:500;margin-bottom:6px">PREDICTED VOLATILITY</div>
                  <div style="display:flex;align-items:baseline;gap:4px">
                    <div class="vol-number" id="singleVolVal">—</div>
                    <div class="vol-unit">%</div>
                  </div>
                </div>
                <div class="vol-meta">
                  <div class="vol-badge" id="singleBadge">—</div>
                  <div class="vol-coin" id="singleCoinLabel"></div>
                  <div class="vol-latency" id="singleLatency"></div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- SECTION: Batch ───────────────────────────────── -->
    <section id="section-batch" style="display:none">
      <div class="page-header">
        <div class="page-title">Batch Analysis</div>
        <div class="page-subtitle">Select multiple coins and compare predicted volatility side-by-side.</div>
      </div>

      <div class="card">
        <div class="card-header">
          <div class="card-title">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/><rect x="14" y="14" width="7" height="7"/></svg>
            Select Coins
          </div>
          <div style="display:flex;gap:8px">
            <button class="btn btn-outlined" style="height:32px;padding:0 16px;font-size:13px" onclick="selectAll()">Select All</button>
            <button class="btn btn-outlined" style="height:32px;padding:0 16px;font-size:13px;border-color:var(--border);color:var(--text-secondary)" onclick="clearAll()">Clear</button>
          </div>
        </div>
        <div class="card-body">
          <div class="chip-group" id="chipGroup">
            {% for s in symbols %}
            <div class="chip" data-sym="{{ s }}" onclick="toggleChip(this)">{{ s.replace('-USD','') }}</div>
            {% endfor %}
          </div>

          <div class="form-row">
            <div class="form-group">
              <label class="form-label">HISTORY PERIOD</label>
              <select class="form-select" id="batchPeriod">
                <option value="3mo">3 Months</option>
                <option value="6mo" selected>6 Months</option>
                <option value="1y">1 Year</option>
              </select>
            </div>
            <div class="form-group">
              <label class="form-label">FORECAST HORIZON (days)</label>
              <input class="form-input" type="number" id="batchHorizon" value="7" min="1" max="30" style="width:140px"/>
            </div>
            <button class="btn btn-primary" id="batchBtn" onclick="predictBatch()">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polygon points="5 3 19 12 5 21 5 3"/></svg>
              Analyse Selected
              <div class="spinner" id="batchSpinner"></div>
            </button>
          </div>

          <div class="progress-bar" id="batchProgress"><div class="progress-fill"></div></div>
          <div class="error-banner" id="batchError">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-2h2v2zm0-4h-2V7h2v6z"/></svg>
            <span id="batchErrorMsg"></span>
          </div>

          <div id="batchResultWrap" style="display:none;margin-top:4px">
            <table class="results-table" id="batchTable">
              <thead>
                <tr>
                  <th>COIN</th>
                  <th>VOLATILITY</th>
                  <th>VISUALIZATION</th>
                  <th>REGIME</th>
                  <th>HORIZON</th>
                </tr>
              </thead>
              <tbody id="batchTbody"></tbody>
            </table>
          </div>
        </div>
      </div>
    </section>

    <!-- SECTION: API Explorer ───────────────────────── -->
    <section id="section-api" style="display:none">
      <div class="page-header">
        <div class="page-title">API Explorer</div>
        <div class="page-subtitle">Browse available endpoints and test them directly.</div>
      </div>
      <div class="card">
        <div class="card-body">
          <div class="info-grid">
            <div>
              <div style="font-size:13px;font-weight:500;margin-bottom:12px;color:var(--text-secondary)">ENDPOINTS</div>
              <div class="info-row"><span class="info-key">GET  /</span><span class="info-val">Root info</span></div>
              <div class="info-row"><span class="info-key">GET  /health</span><span class="info-val">Health check</span></div>
              <div class="info-row"><span class="info-key">POST /predict</span><span class="info-val">Single prediction</span></div>
              <div class="info-row"><span class="info-key">POST /predict/batch</span><span class="info-val">Batch prediction</span></div>
              <div class="info-row"><span class="info-key">POST /predict/features</span><span class="info-val">Custom features</span></div>
              <div class="info-row"><span class="info-key">GET  /model/info</span><span class="info-val">Model metadata</span></div>
              <div class="info-row"><span class="info-key">GET  /symbols</span><span class="info-val">Supported coins</span></div>
              <div class="info-row"><span class="info-key">GET  /docs</span><span class="info-val">Swagger UI</span></div>
            </div>
            <div>
              <div style="font-size:13px;font-weight:500;margin-bottom:12px;color:var(--text-secondary)">QUICK LINKS</div>
              <div style="display:flex;flex-direction:column;gap:10px">
                <a href="{{ fastapi_url }}/docs" target="_blank" class="btn btn-outlined" style="text-decoration:none;width:fit-content">
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M18 13v6a2 2 0 01-2 2H5a2 2 0 01-2-2V8a2 2 0 012-2h6"/><polyline points="15 3 21 3 21 9"/><line x1="10" y1="14" x2="21" y2="3"/></svg>
                  Open Swagger UI
                </a>
                <a href="{{ fastapi_url }}/health" target="_blank" class="btn btn-outlined" style="text-decoration:none;width:fit-content">
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 12h-4l-3 9L9 3l-3 9H2"/></svg>
                  Health Endpoint
                </a>
                <a href="{{ fastapi_url }}/model/info" target="_blank" class="btn btn-outlined" style="text-decoration:none;width:fit-content">
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>
                  Model Info
                </a>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- SECTION: Health ─────────────────────────────── -->
    <section id="section-health" style="display:none">
      <div class="page-header">
        <div class="page-title">Health Monitor</div>
        <div class="page-subtitle">Real-time status of all services.</div>
      </div>
      <div class="card">
        <div class="card-body" id="healthBody">
          <div class="empty-state">
            <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M22 12h-4l-3 9L9 3l-3 9H2"/></svg>
            <p>Loading health data…</p>
          </div>
        </div>
      </div>
    </section>

  </main>
</div>

<!-- Toast Container -->
<div class="toast-container" id="toastContainer"></div>

<script>
  const API = "{{ fastapi_url }}";

  // ── Navigation ──────────────────────────────────────────────────────────────
  function showSection(id) {
    ['single','batch','api','health'].forEach(s => {
      document.getElementById('section-'+s).style.display = s===id ? '' : 'none';
    });
    document.querySelectorAll('.nav-item').forEach((el, i) => {
      el.classList.toggle('active', i === ['single','batch','api','health'].indexOf(id));
    });
    if (id === 'health') loadHealth();
  }

  // ── Toast ───────────────────────────────────────────────────────────────────
  function toast(msg, isError=false) {
    const t = document.createElement('div');
    t.className = 'toast' + (isError ? ' error' : '');
    t.textContent = msg;
    document.getElementById('toastContainer').appendChild(t);
    setTimeout(() => t.remove(), 4000);
  }

  // ── Status Check ────────────────────────────────────────────────────────────
  async function checkStatus() {
    const pill = document.getElementById('statusPill');
    const txt  = document.getElementById('statusText');
    const met  = document.getElementById('metricStatus');
    const sub  = document.getElementById('metricSub');
    try {
      const r = await fetch('/api/health', {signal: AbortSignal.timeout(5000)});
      const d = await r.json();
      if (d.status === 'ok' || d.model_loaded !== undefined) {
        pill.className = 'status-pill online';
        txt.textContent = 'API Online';
        met.textContent = 'UP';
        sub.textContent = 'FastAPI responding';
      } else throw new Error();
    } catch {
      pill.className = 'status-pill offline';
      txt.textContent = 'API Offline';
      met.textContent = 'DOWN';
      sub.textContent = 'Cannot reach FastAPI';
    }
  }

  // ── Single Prediction ───────────────────────────────────────────────────────
  async function predictSingle() {
    const sym     = document.getElementById('singleSymbol').value;
    const period  = document.getElementById('singlePeriod').value;
    const horizon = parseInt(document.getElementById('singleHorizon').value) || 7;
    const btn     = document.getElementById('singleBtn');
    const spinner = document.getElementById('singleSpinner');
    const errEl   = document.getElementById('singleError');
    const errMsg  = document.getElementById('singleErrorMsg');
    const resEl   = document.getElementById('singleResult');
    const progEl  = document.getElementById('singleProgress');

    btn.disabled = true; spinner.style.display = 'block';
    errEl.classList.remove('visible'); resEl.classList.remove('visible');
    progEl.classList.add('active');

    const t0 = Date.now();
    try {
      const res = await fetch('/api/predict', {
        method: 'POST',
        headers: {'Content-Type':'application/json'},
        body: JSON.stringify({symbol: sym, period, horizon_days: horizon})
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || 'Prediction failed');

      const latency = Date.now() - t0;
      const vol = (data.predicted_volatility * 100).toFixed(2);
      const regime = (data.volatility_regime || '').toLowerCase();

      document.getElementById('singleVolVal').textContent = vol;
      document.getElementById('singleResultTitle').textContent = `${sym.replace('-USD','')} · ${horizon}-day forecast`;
      document.getElementById('singleCoinLabel').textContent = `${period} history  ·  horizon ${horizon}d`;
      document.getElementById('singleLatency').textContent = `Response time: ${latency}ms`;
      document.getElementById('singleTimestamp').textContent = new Date().toLocaleTimeString();

      const badge = document.getElementById('singleBadge');
      badge.className = 'vol-badge';
      if (regime.includes('low'))  { badge.classList.add('badge-low');    badge.textContent = '🟢 Low Volatility'; }
      else if (regime.includes('high')) { badge.classList.add('badge-high');  badge.textContent = '🔴 High Volatility'; }
      else                         { badge.classList.add('badge-medium'); badge.textContent = '🟡 Medium Volatility'; }

      resEl.classList.add('visible');
    } catch(e) {
      errMsg.textContent = e.message;
      errEl.classList.add('visible');
      toast(e.message, true);
    } finally {
      btn.disabled = false; spinner.style.display = 'none';
      progEl.classList.remove('active');
    }
  }

  // ── Chip Selection ──────────────────────────────────────────────────────────
  function toggleChip(el) { el.classList.toggle('selected'); }
  function selectAll()    { document.querySelectorAll('.chip').forEach(c => c.classList.add('selected')); }
  function clearAll()     { document.querySelectorAll('.chip').forEach(c => c.classList.remove('selected')); }

  // ── Batch Prediction ────────────────────────────────────────────────────────
  async function predictBatch() {
    const selected = [...document.querySelectorAll('.chip.selected')].map(c => c.dataset.sym);
    if (!selected.length) { toast('Please select at least one coin.', true); return; }

    const period  = document.getElementById('batchPeriod').value;
    const horizon = parseInt(document.getElementById('batchHorizon').value) || 7;
    const btn     = document.getElementById('batchBtn');
    const spinner = document.getElementById('batchSpinner');
    const errEl   = document.getElementById('batchError');
    const errMsg  = document.getElementById('batchErrorMsg');
    const wrap    = document.getElementById('batchResultWrap');
    const tbody   = document.getElementById('batchTbody');
    const prog    = document.getElementById('batchProgress');

    btn.disabled = true; spinner.style.display = 'block';
    errEl.classList.remove('visible'); wrap.style.display = 'none';
    prog.classList.add('active');

    try {
      const res = await fetch('/api/predict/batch?' + new URLSearchParams({period, horizon_days: horizon}), {
        method: 'POST',
        headers: {'Content-Type':'application/json'},
        body: JSON.stringify({symbols: selected})
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || 'Batch prediction failed');

      const rows = data.predictions || data;
      const maxVol = Math.max(...rows.map(r => r.predicted_volatility));
      tbody.innerHTML = '';

      rows.sort((a,b) => b.predicted_volatility - a.predicted_volatility)
          .forEach(r => {
        const vol   = (r.predicted_volatility * 100).toFixed(3);
        const regime = (r.volatility_regime || '').toLowerCase();
        let badge, cls;
        if (regime.includes('low'))       { badge='🟢 Low';    cls='badge-low'; }
        else if (regime.includes('high')) { badge='🔴 High';   cls='badge-high'; }
        else                               { badge='🟡 Medium'; cls='badge-medium'; }

        const barW = Math.max(4, Math.round((r.predicted_volatility/maxVol)*120));
        tbody.insertAdjacentHTML('beforeend', `
          <tr>
            <td><strong>${r.symbol.replace('-USD','')}</strong></td>
            <td><span style="font-variant-numeric:tabular-nums;font-family:var(--font-mono)">${vol}%</span></td>
            <td><div class="vol-bar-wrap"><div class="vol-bar" style="width:${barW}px"></div><span style="font-size:12px;color:var(--text-hint)">${vol}</span></div></td>
            <td><span class="vol-badge ${cls}" style="padding:3px 10px;font-size:12px">${badge}</span></td>
            <td style="color:var(--text-secondary)">${horizon}d</td>
          </tr>`);
      });
      wrap.style.display = '';
    } catch(e) {
      errMsg.textContent = e.message;
      errEl.classList.add('visible');
      toast(e.message, true);
    } finally {
      btn.disabled = false; spinner.style.display = 'none';
      prog.classList.remove('active');
    }
  }

  // ── Health Monitor ──────────────────────────────────────────────────────────
  async function loadHealth() {
    const body = document.getElementById('healthBody');
    try {
      const res  = await fetch('/api/health');
      const data = await res.json();
      body.innerHTML = `
        <div style="display:flex;flex-direction:column;gap:12px">
          <div class="info-row"><span class="info-key">FastAPI Status</span><span class="info-val" style="color:var(--green)">● Online</span></div>
          <div class="info-row"><span class="info-key">Model Loaded</span><span class="info-val">${data.model_loaded ?? data.status}</span></div>
          <div class="info-row"><span class="info-key">Checked At</span><span class="info-val">${new Date().toLocaleString()}</span></div>
          <div class="info-row"><span class="info-key">API Base URL</span><span class="info-val">${API}</span></div>
        </div>`;
    } catch {
      body.innerHTML = `<div class="error-banner visible">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-2h2v2zm0-4h-2V7h2v6z"/></svg>
        Cannot reach FastAPI at ${API}
      </div>`;
    }
  }

  // ── Init ────────────────────────────────────────────────────────────────────
  checkStatus();
  setInterval(checkStatus, 30000);
</script>
</body>
</html>
"""

# ── Routes ────────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    return render_template_string(
        HTML,
        symbols=SUPPORTED_SYMBOLS,
        fastapi_url=FASTAPI_URL,
    )


@app.route("/api/health")
def health():
    """Proxy health check to FastAPI."""
    try:
        r = requests.get(f"{FASTAPI_URL}/health", timeout=5)
        return jsonify(r.json()), r.status_code
    except Exception as e:
        return jsonify({"status": "error", "detail": str(e)}), 503


@app.route("/api/predict", methods=["POST"])
def predict():
    """Proxy single-coin prediction to FastAPI."""
    try:
        payload = request.get_json()
        r = requests.post(f"{FASTAPI_URL}/predict", json=payload, timeout=60)
        return jsonify(r.json()), r.status_code
    except Exception as e:
        return jsonify({"detail": str(e)}), 503


@app.route("/api/predict/batch", methods=["POST"])
def predict_batch():
    """Proxy batch prediction to FastAPI."""
    try:
        payload  = request.get_json()
        params   = request.args.to_dict()
        r = requests.post(
            f"{FASTAPI_URL}/predict/batch",
            json=payload, params=params, timeout=120
        )
        return jsonify(r.json()), r.status_code
    except Exception as e:
        return jsonify({"detail": str(e)}), 503


@app.route("/api/model/info")
def model_info():
    try:
        r = requests.get(f"{FASTAPI_URL}/model/info", timeout=5)
        return jsonify(r.json()), r.status_code
    except Exception as e:
        return jsonify({"detail": str(e)}), 503


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=PORT, debug=False)