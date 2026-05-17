#!/usr/bin/env python3
# ============================================================
# monitoring.py — Health Check & Uptime Monitor
# Cryptocurrency Volatility Predictor
# ============================================================
# Run: python3 monitoring.py
# ============================================================

import time
import logging
import requests
from datetime import datetime

# ── Logging setup ─────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[
        logging.FileHandler("/var/log/crypto_monitor.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# ── Services to monitor ───────────────────────────────────────
SERVICES = {
    "FastAPI Health" : "http://localhost:8000/health",
    "FastAPI Root"   : "http://localhost:8000/",
    "Flask UI"       : "http://localhost:5000/",
    "Streamlit"      : "http://localhost:8501/",
}

# ── Check interval (seconds) ──────────────────────────────────
CHECK_INTERVAL = 60   # check every 60 seconds

# ── Alert threshold ───────────────────────────────────────────
TIMEOUT = 10          # seconds

def check_service(name: str, url: str) -> dict:
    """Check if a service is up and responding."""
    try:
        start = time.time()
        response = requests.get(url, timeout=TIMEOUT)
        latency = round((time.time() - start) * 1000, 2)

        status = "✅ UP" if response.status_code < 400 else "⚠️  DEGRADED"
        logger.info(f"{status} | {name:<20} | {response.status_code} | {latency}ms")

        return {
            "service"     : name,
            "url"         : url,
            "status"      : "up",
            "status_code" : response.status_code,
            "latency_ms"  : latency,
            "timestamp"   : datetime.utcnow().isoformat()
        }

    except requests.exceptions.ConnectionError:
        logger.error(f"🔴 DOWN | {name:<20} | Connection refused")
        return {"service": name, "status": "down", "error": "Connection refused"}

    except requests.exceptions.Timeout:
        logger.error(f"🔴 TIMEOUT | {name:<20} | No response in {TIMEOUT}s")
        return {"service": name, "status": "timeout", "error": f"Timeout after {TIMEOUT}s"}

    except Exception as e:
        logger.error(f"🔴 ERROR | {name:<20} | {e}")
        return {"service": name, "status": "error", "error": str(e)}


def run_health_check():
    """Run health check for all services."""
    print(f"\n{'='*60}")
    print(f"Health Check — {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC")
    print(f"{'='*60}")

    results = []
    for name, url in SERVICES.items():
        result = check_service(name, url)
        results.append(result)

    # Summary
    up_count   = sum(1 for r in results if r["status"] == "up")
    down_count = len(results) - up_count

    print(f"\n📊 Summary: {up_count}/{len(results)} services UP")
    if down_count > 0:
        print(f"⚠️  {down_count} service(s) need attention!")

    return results


def monitor_predictions():
    """Test the prediction endpoint."""
    try:
        response = requests.post(
            "http://localhost:8000/predict",
            json={"symbol": "BTC-USD", "period": "3mo", "horizon": 7},
            timeout=60
        )
        if response.status_code == 200:
            data = response.json()
            logger.info(
                f"🤖 Prediction OK | BTC-USD | "
                f"Vol={data.get('predicted_volatility', 'N/A')} | "
                f"Regime={data.get('volatility_regime', 'N/A')} | "
                f"Latency={data.get('latency_ms', 'N/A')}ms"
            )
        else:
            logger.warning(f"⚠️  Prediction endpoint returned {response.status_code}")
    except Exception as e:
        logger.error(f"🔴 Prediction test failed: {e}")


if __name__ == "__main__":
    logger.info("🚀 Starting Crypto Volatility Predictor Monitor...")
    logger.info(f"   Checking {len(SERVICES)} services every {CHECK_INTERVAL}s")

    check_count = 0
    while True:
        check_count += 1
        run_health_check()

        # Test prediction every 5 checks (every 5 minutes)
        if check_count % 5 == 0:
            logger.info("🤖 Running prediction test...")
            monitor_predictions()

        time.sleep(CHECK_INTERVAL)
