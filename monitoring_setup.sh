#!/bin/bash
# ============================================================
# Step 6 — Monitoring Setup Script
# Cryptocurrency Volatility Predictor
# ============================================================
# Run this on your EC2 server:
#   chmod +x monitoring_setup.sh
#   ./monitoring_setup.sh
# ============================================================

echo "🚀 Setting up Monitoring on AWS EC2..."

# ── 1. Install CloudWatch Agent ───────────────────────────────
echo "📦 Installing CloudWatch Agent..."
wget -q https://s3.amazonaws.com/amazoncloudwatch-agent/ubuntu/amd64/latest/amazon-cloudwatch-agent.deb
sudo dpkg -i amazon-cloudwatch-agent.deb
rm amazon-cloudwatch-agent.deb

# ── 2. Create CloudWatch config ───────────────────────────────
echo "⚙️  Creating CloudWatch config..."
sudo mkdir -p /opt/aws/amazon-cloudwatch-agent/etc/

sudo tee /opt/aws/amazon-cloudwatch-agent/etc/amazon-cloudwatch-agent.json > /dev/null <<'EOF'
{
  "metrics": {
    "namespace": "CryptoVolPredictor",
    "metrics_collected": {
      "cpu": {
        "measurement": ["cpu_usage_idle", "cpu_usage_user", "cpu_usage_system"],
        "metrics_collection_interval": 60,
        "totalcpu": true
      },
      "mem": {
        "measurement": ["mem_used_percent", "mem_available"],
        "metrics_collection_interval": 60
      },
      "disk": {
        "measurement": ["disk_used_percent"],
        "metrics_collection_interval": 60,
        "resources": ["/"]
      }
    }
  },
  "logs": {
    "logs_collected": {
      "files": {
        "collect_list": [
          {
            "file_path": "/var/log/crypto_fastapi.log",
            "log_group_name": "/crypto-vol/fastapi",
            "log_stream_name": "{instance_id}"
          },
          {
            "file_path": "/var/log/crypto_flask.log",
            "log_group_name": "/crypto-vol/flask",
            "log_stream_name": "{instance_id}"
          }
        ]
      }
    }
  }
}
EOF

# ── 3. Start CloudWatch Agent ─────────────────────────────────
echo "▶️  Starting CloudWatch Agent..."
sudo /opt/aws/amazon-cloudwatch-agent/bin/amazon-cloudwatch-agent-ctl \
  -a fetch-config \
  -m ec2 \
  -c file:/opt/aws/amazon-cloudwatch-agent/etc/amazon-cloudwatch-agent.json \
  -s

# ── 4. Create log files ───────────────────────────────────────
sudo touch /var/log/crypto_fastapi.log
sudo touch /var/log/crypto_flask.log
sudo chmod 666 /var/log/crypto_fastapi.log
sudo chmod 666 /var/log/crypto_flask.log

echo "✅ CloudWatch Monitoring setup complete!"
echo ""
echo "📊 View metrics at:"
echo "   AWS Console → CloudWatch → Metrics → CryptoVolPredictor"
echo "   AWS Console → CloudWatch → Log groups → /crypto-vol/fastapi"
