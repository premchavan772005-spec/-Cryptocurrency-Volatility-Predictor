# ============================================================
# Cryptocurrency Volatility Predictor — Flask Web UI
# ============================================================
# Run locally:  python flask_app.py
# Opens at:     http://localhost:5000
# ============================================================

import os
import requests
from flask import Flask, render_template_string, request, jsonify

app = Flask(__name__)

# ── FastAPI backend URL ───────────────────────────────────────
FASTAPI_URL = os.getenv("FASTAPI_URL", "http://localhost:8000")

# ── Supported symbols ─────────────────────────────────────────
SYMBOLS = [
    "BTC-USD", "ETH-USD", "BNB-USD", "ADA-USD", "XRP-USD",
    "SOL-USD", "DOGE-USD", "DOT-USD", "MATIC-USD", "LTC-USD",
    "AVAX-USD", "LINK-USD", "ATOM-USD", "UNI-USD", "XLM-USD",
]

# ══════════════════════════════════════════════════════════════
# HTML TEMPLATE
# ══════════════════════════════════════════════════════════════
HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>Crypto Volatility Predictor</title>
  <style>
    * { box-sizing: border-box; margin: 0; padding: 0; }

    body {
      font-family: 'Segoe UI', sans-serif;
      background: #0f172a;
      color: #e2e8f0;
      min-height: 100vh;
    }

    /* ── Navbar ── */
    nav {
      background: #1e293b;
      padding: 16px 32px;
      display: flex;
      align-items: center;
      gap: 12px;
      border-bottom: 1px solid #334155;
    }
    nav .logo { font-size: 22px; font-weight: 700; color: #f59e0b; }
    nav .sub  { font-size: 13px; color: #94a3b8; }

    /* ── Main container ── */
    .container { max-width: 900px; margin: 40px auto; padding: 0 20px; }

    /* ── Card ── */
    .card {
      background: #1e293b;
      border: 1px solid #334155;
      border-radius: 16px;
      padding: 32px;
      margin-bottom: 24px;
    }
    .card h2 { font-size: 18px; color: #f1f5f9; margin-bottom: 20px; }

    /* ── Form ── */
    .form-grid {
      display: grid;
      grid-template-columns: 1fr 1fr 1fr;
      gap: 16px;
      margin-bottom: 24px;
    }
    label { font-size: 13px; color: #94a3b8; display: block; margin-bottom: 6px; }
    select, input {
      width: 100%;
      background: #0f172a;
      border: 1px solid #334155;
      color: #e2e8f0;
      padding: 10px 14px;
      border-radius: 8px;
      font-size: 14px;
      outline: none;
    }
    select:focus, input:focus { border-color: #f59e0b; }

    /* ── Button ── */
    .btn {
      background: #f59e0b;
      color: #0f172a;
      border: none;
      padding: 12px 32px;
      border-radius: 8px;
      font-size: 15px;
      font-weight: 700;
      cursor: pointer;
      width: 100%;
      transition: background 0.2s;
    }
    .btn:hover { background: #d97706; }
    .btn:disabled { background: #475569; cursor: not-allowed; }

    /* ── Result cards ── */
    .result-grid {
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 16px;
      margin-top: 24px;
    }
    .metric {
      background: #0f172a;
      border: 1px solid #334155;
      border-radius: 12px;
      padding: 20px;
      text-align: center;
    }
    .metric .label { font-size: 12px; color: #64748b; margin-bottom: 8px; }
    .metric .value { font-size: 26px; font-weight: 700; color: #f1f5f9; }
    .metric .sub   { font-size: 12px; color: #94a3b8; margin-top: 4px; }

    /* ── Regime badge ── */
    .badge {
      display: inline-block;
      padding: 6px 20px;
      border-radius: 999px;
      font-size: 14px;
      font-weight: 700;
      margin-top: 8px;
    }
    .badge.low    { background: #14532d; color: #4ade80; }
    .badge.medium { background: #713f12; color: #fbbf24; }
    .badge.high   { background: #7f1d1d; color: #f87171; }

    /* ── Batch section ── */
    .batch-grid { display: grid; grid-template-columns: repeat(5, 1fr); gap: 8px; margin-bottom: 16px; }
    .batch-chip {
      background: #0f172a;
      border: 1px solid #334155;
      border-radius: 8px;
      padding: 8px;
      text-align: center;
      font-size: 12px;
      cursor: pointer;
      transition: border-color 0.2s;
    }
    .batch-chip.selected { border-color: #f59e0b; color: #f59e0b; }

    /* ── Table ── */
    table { width: 100%; border-collapse: collapse; margin-top: 16px; font-size: 13px; }
    th { background: #0f172a; color: #64748b; padding: 10px 12px; text-align: left; }
    td { padding: 10px 12px; border-bottom: 1px solid #1e293b; }
    tr:hover td { background: #1e293b22; }

    /* ── Spinner ── */
    .spinner {
      display: none;
      width: 20px; height: 20px;
      border: 3px solid #334155;
      border-top-color: #f59e0b;
      border-radius: 50%;
      animation: spin 0.7s linear infinite;
      margin: 0 auto;
    }
    @keyframes spin { to { transform: rotate(360deg); } }

    /* ── Error ── */
    .error { background: #7f1d1d22; border: 1px solid #7f1d1d; color: #f87171;
             padding: 12px 16px; border-radius: 8px; margin-top: 16px; font-size: 13px; }

    /* ── Health dot ── */
    .health-dot {
      width: 8px; height: 8px; border-radius: 50%;
      background: #4ade80; display: inline-block; margin-right: 6px;
    }
    .health-dot.red { background: #f87171; }

    .hidden { display: none; }
    @media(max-width: 600px) {
      .form-grid { grid-template-columns: 1fr; }
      .result-grid { grid-template-columns: 1fr; }
      .batch-grid { grid-template-columns: repeat(3, 1fr); }
    }
  </style>
</head>
<body>

<!-- Navbar -->
<nav>
  <div>
    <div class="logo">📈 CryptoVol</div>
    <div class="sub">Volatility Prediction Dashboard</div>
  </div>
  <div style="margin-left:auto; font-size:13px; color:#94a3b8;">
    <span class="health-dot" id="health-dot"></span>
    <span id="health-status">Checking API...</span>
  </div>
</nav>

<div class="container">

  <!-- ── Single Prediction Card ── -->
  <div class="card">
    <h2>🔮 Single Coin Prediction</h2>

    <div class="form-grid">
      <div>
        <label>Cryptocurrency</label>
        <select id="symbol">
          {% for s in symbols %}
          <option value="{{ s }}">{{ s.replace('-USD','') }}</option>
          {% endfor %}
        </select>
      </div>
      <div>
        <label>History Period</label>
        <select id="period">
          <option value="3mo">3 Months</option>
          <option value="6mo" selected>6 Months</option>
          <option value="1y">1 Year</option>
          <option value="2y">2 Years</option>
        </select>
      </div>
      <div>
        <label>Forecast Horizon (days)</label>
        <input type="number" id="horizon" value="7" min="1" max="30"/>
      </div>
    </div>

    <button class="btn" id="predict-btn" onclick="predict()">🚀 Predict Volatility</button>

    <div class="spinner" id="spinner" style="margin-top:20px;"></div>
    <div class="error hidden" id="error-box"></div>

    <!-- Result -->
    <div class="hidden" id="result-box">
      <div class="result-grid">
        <div class="metric">
          <div class="label">Predicted Volatility</div>
          <div class="value" id="res-vol">—</div>
          <div class="sub">Annualised</div>
        </div>
        <div class="metric">
          <div class="label">Volatility Regime</div>
          <div class="value" id="res-emoji">—</div>
          <div><span class="badge" id="res-badge">—</span></div>
        </div>
        <div class="metric">
          <div class="label">Response Time</div>
          <div class="value" id="res-latency">—</div>
          <div class="sub">milliseconds</div>
        </div>
      </div>
      <div style="margin-top:16px; font-size:12px; color:#475569;">
        Prediction date: <span id="res-date">—</span> &nbsp;|&nbsp;
        Model version: <span id="res-model">—</span>
      </div>
    </div>
  </div>

  <!-- ── Batch Prediction Card ── -->
  <div class="card">
    <h2>📊 Batch Prediction</h2>
    <p style="font-size:13px; color:#64748b; margin-bottom:16px;">
      Select multiple coins and predict all at once.
    </p>

    <div class="batch-grid" id="batch-chips">
      {% for s in symbols %}
      <div class="batch-chip" onclick="toggleChip(this)" data-sym="{{ s }}">
        {{ s.replace('-USD','') }}
      </div>
      {% endfor %}
    </div>

    <button class="btn" onclick="batchPredict()" style="margin-bottom:8px;">
      ⚡ Predict All Selected
    </button>

    <div class="spinner hidden" id="batch-spinner"></div>
    <div class="error hidden" id="batch-error"></div>

    <div class="hidden" id="batch-result">
      <table>
        <thead>
          <tr>
            <th>Coin</th>
            <th>Predicted Volatility</th>
            <th>Regime</th>
            <th>Status</th>
          </tr>
        </thead>
        <tbody id="batch-tbody"></tbody>
      </table>
    </div>
  </div>

</div><!-- /container -->

<script>
// ── Health check ──────────────────────────────────────────────
async function checkHealth() {
  try {
    const r = await fetch("/api/health");
    const d = await r.json();
    if (d.status === "ok") {
      document.getElementById("health-dot").className    = "health-dot";
      document.getElementById("health-status").innerText = "API Online";
    } else { throw new Error(); }
  } catch {
    document.getElementById("health-dot").className    = "health-dot red";
    document.getElementById("health-status").innerText = "API Offline";
  }
}
checkHealth();
setInterval(checkHealth, 30000);

// ── Single prediction ─────────────────────────────────────────
async function predict() {
  const btn     = document.getElementById("predict-btn");
  const spinner = document.getElementById("spinner");
  const errBox  = document.getElementById("error-box");
  const resBox  = document.getElementById("result-box");

  btn.disabled  = true;
  spinner.style.display = "block";
  errBox.classList.add("hidden");
  resBox.classList.add("hidden");

  const payload = {
    symbol  : document.getElementById("symbol").value,
    period  : document.getElementById("period").value,
    horizon : parseInt(document.getElementById("horizon").value),
  };

  try {
    const r = await fetch("/api/predict", {
      method  : "POST",
      headers : { "Content-Type": "application/json" },
      body    : JSON.stringify(payload),
    });
    const d = await r.json();
    if (!r.ok) throw new Error(d.detail || "Prediction failed");

    document.getElementById("res-vol").innerText     = d.predicted_volatility.toFixed(4);
    document.getElementById("res-emoji").innerText   = d.regime_emoji;
    document.getElementById("res-latency").innerText = d.latency_ms + " ms";
    document.getElementById("res-date").innerText    = d.prediction_date;
    document.getElementById("res-model").innerText   = d.model_version;

    const badge = document.getElementById("res-badge");
    badge.innerText   = d.volatility_regime;
    badge.className   = "badge " + d.volatility_regime.toLowerCase();

    resBox.classList.remove("hidden");
  } catch(e) {
    errBox.innerText = "❌ Error: " + e.message;
    errBox.classList.remove("hidden");
  } finally {
    btn.disabled = false;
    spinner.style.display = "none";
  }
}

// ── Batch chip toggle ─────────────────────────────────────────
function toggleChip(el) { el.classList.toggle("selected"); }

// ── Batch prediction ──────────────────────────────────────────
async function batchPredict() {
  const chips   = document.querySelectorAll(".batch-chip.selected");
  const symbols = Array.from(chips).map(c => c.dataset.sym);
  if (!symbols.length) { alert("Please select at least one coin!"); return; }

  const spinner = document.getElementById("batch-spinner");
  const errBox  = document.getElementById("batch-error");
  const resDiv  = document.getElementById("batch-result");
  const tbody   = document.getElementById("batch-tbody");

  spinner.classList.remove("hidden");
  errBox.classList.add("hidden");
  resDiv.classList.add("hidden");

  try {
    const r = await fetch("/api/predict/batch", {
      method  : "POST",
      headers : { "Content-Type": "application/json" },
      body    : JSON.stringify({ symbols }),
    });
    const d = await r.json();
    if (!r.ok) throw new Error(d.detail || "Batch failed");

    tbody.innerHTML = d.results.map(row => {
      if (row.status === "error") {
        return `<tr>
          <td>${row.symbol}</td>
          <td colspan="2" style="color:#f87171">${row.detail}</td>
          <td>❌ Error</td>
        </tr>`;
      }
      const cls = row.volatility_regime.toLowerCase();
      return `<tr>
        <td><strong>${row.symbol.replace("-USD","")}</strong></td>
        <td>${row.predicted_volatility.toFixed(4)}</td>
        <td><span class="badge ${cls}">${row.regime_emoji} ${row.volatility_regime}</span></td>
        <td style="color:#4ade80">✅ OK</td>
      </tr>`;
    }).join("");

    resDiv.classList.remove("hidden");
  } catch(e) {
    errBox.innerText = "❌ Error: " + e.message;
    errBox.classList.remove("hidden");
  } finally {
    spinner.classList.add("hidden");
  }
}
</script>
</body>
</html>
"""

# ══════════════════════════════════════════════════════════════
# ROUTES
# ══════════════════════════════════════════════════════════════

# ── Main page ─────────────────────────────────────────────────
@app.route("/")
def index():
    return render_template_string(HTML, symbols=SYMBOLS)


# ── Proxy: health ─────────────────────────────────────────────
@app.route("/api/health")
def health():
    try:
        r = requests.get(f"{FASTAPI_URL}/health", timeout=5)
        return jsonify(r.json()), r.status_code
    except Exception as e:
        return jsonify({"status": "error", "detail": str(e)}), 503


# ── Proxy: single predict ─────────────────────────────────────
@app.route("/api/predict", methods=["POST"])
def predict():
    try:
        payload = request.get_json()
        r = requests.post(f"{FASTAPI_URL}/predict", json=payload, timeout=60)
        return jsonify(r.json()), r.status_code
    except Exception as e:
        return jsonify({"detail": str(e)}), 500


# ── Proxy: batch predict ──────────────────────────────────────
@app.route("/api/predict/batch", methods=["POST"])
def batch():
    try:
        data    = request.get_json()
        symbols = data.get("symbols", [])
        r = requests.post(
            f"{FASTAPI_URL}/predict/batch",
            json=symbols,
            params={"period": data.get("period", "6mo"), "horizon": data.get("horizon", 7)},
            timeout=120
        )
        return jsonify(r.json()), r.status_code
    except Exception as e:
        return jsonify({"detail": str(e)}), 500


# ── Run ───────────────────────────────────────────────────────
if __name__ == "__main__":
    port = int(os.getenv("FLASK_PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
