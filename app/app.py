"""
Flask Web Uygulaması - CI/CD Demo
Render (PaaS) üzerinde Docker ile deploy edilecek.
"""

from flask import Flask, render_template_string
import datetime
import os

app = Flask(__name__)

# ─── HTML Şablonu ───────────────────────────────────────────────
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CI/CD Demo - Render</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap" rel="stylesheet">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Inter', sans-serif;
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
            color: #fff;
        }
        .card {
            background: rgba(255,255,255,0.05);
            backdrop-filter: blur(20px);
            border: 1px solid rgba(255,255,255,0.1);
            border-radius: 24px;
            padding: 48px 56px;
            max-width: 560px;
            width: 90%;
            text-align: center;
            box-shadow: 0 8px 32px rgba(0,0,0,0.4);
        }
        .badge {
            display: inline-block;
            background: linear-gradient(135deg, #00d2ff, #3a7bd5);
            padding: 6px 18px;
            border-radius: 50px;
            font-size: 12px;
            font-weight: 600;
            letter-spacing: 1.5px;
            text-transform: uppercase;
            margin-bottom: 24px;
        }
        h1 {
            font-size: 2rem;
            font-weight: 700;
            margin-bottom: 12px;
            background: linear-gradient(90deg, #00d2ff, #a855f7);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        .subtitle {
            color: rgba(255,255,255,0.6);
            font-size: 1rem;
            margin-bottom: 32px;
            line-height: 1.6;
        }
        .info-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 16px;
            margin-bottom: 32px;
        }
        .info-item {
            background: rgba(255,255,255,0.05);
            border-radius: 16px;
            padding: 20px 16px;
            border: 1px solid rgba(255,255,255,0.08);
        }
        .info-item .label {
            font-size: 11px;
            text-transform: uppercase;
            letter-spacing: 1px;
            color: rgba(255,255,255,0.4);
            margin-bottom: 8px;
        }
        .info-item .value {
            font-size: 14px;
            font-weight: 600;
            color: #00d2ff;
        }
        .pipeline {
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 8px;
            flex-wrap: wrap;
        }
        .step {
            background: rgba(255,255,255,0.08);
            border-radius: 12px;
            padding: 10px 16px;
            font-size: 12px;
            font-weight: 600;
            border: 1px solid rgba(255,255,255,0.1);
        }
        .step.active {
            background: linear-gradient(135deg, #00d2ff33, #3a7bd533);
            border-color: #00d2ff;
            color: #00d2ff;
        }
        .arrow { color: rgba(255,255,255,0.3); font-size: 18px; }
        .version {
            margin-top: 24px;
            font-size: 12px;
            color: rgba(255,255,255,0.3);
        }
    </style>
</head>
<body>
    <div class="card">
        <div class="badge">🚀 Canlı Yayında</div>
        <h1>CI/CD Pipeline Demo</h1>
        <p class="subtitle">
            Bu uygulama GitHub Actions ve Docker ile build edilip<br>
            Render PaaS platformuna otomatik olarak deploy edilmiştir.
        </p>
        <div class="info-grid">
            <div class="info-item">
                <div class="label">Sunucu Zamanı</div>
                <div class="value">{{ server_time }}</div>
            </div>
            <div class="info-item">
                <div class="label">Hostname</div>
                <div class="value">{{ hostname }}</div>
            </div>
            <div class="info-item">
                <div class="label">Platform</div>
                <div class="value">Render PaaS ☁️</div>
            </div>
            <div class="info-item">
                <div class="label">Container</div>
                <div class="value">Docker 🐳</div>
            </div>
        </div>
        <div class="pipeline">
            <div class="step active">GitHub Push</div>
            <span class="arrow">→</span>
            <div class="step active">Docker Build</div>
            <span class="arrow">→</span>
            <div class="step active">Docker Hub</div>
            <span class="arrow">→</span>
            <div class="step active">Render Deploy</div>
        </div>
        <p class="version">v1.0.0 • Flask + Docker + GitHub Actions + Render</p>
    </div>
</body>
</html>
"""


@app.route("/")
def home():
    """Ana sayfa - Pipeline durumunu gösteren dashboard."""
    return render_template_string(
        HTML_TEMPLATE,
        server_time=datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
        hostname=os.uname().nodename if hasattr(os, "uname") else os.environ.get("COMPUTERNAME", "unknown"),
    )


@app.route("/health")
def health():
    """Sağlık kontrolü endpoint'i."""
    return {"status": "healthy", "timestamp": datetime.datetime.now().isoformat()}, 200


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
