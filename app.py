from fastapi import FastAPI
from fastapi.responses import HTMLResponse

app = FastAPI(title="IAiOS SCADA Dashboard")


@app.get("/", response_class=HTMLResponse)
def dashboard() -> HTMLResponse:
    html = """
<!doctype html>
<html lang=\"en\">
<head>
  <meta charset=\"utf-8\" />
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
  <title>IAiOS | Industrial SCADA Dashboard</title>
  <script src=\"https://cdn.jsdelivr.net/npm/chart.js@4.4.1/dist/chart.umd.min.js\"></script>
  <style>
    :root {
      --bg: #0b0f14;
      --panel: #121922;
      --panel-2: #17212e;
      --text: #e8edf2;
      --muted: #92a0af;
      --border: #243243;
      --ok: #1fd479;
      --warn: #f4b740;
      --danger: #ff5d5d;
      --accent: #3aa0ff;
    }

    * { box-sizing: border-box; }

    body {
      margin: 0;
      min-height: 100vh;
      background: radial-gradient(circle at top right, #101826 0%, var(--bg) 45%);
      color: var(--text);
      font-family: Inter, Segoe UI, Roboto, Arial, sans-serif;
    }

    .container {
      max-width: 1200px;
      margin: 0 auto;
      padding: 22px;
    }

    .header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      gap: 16px;
      margin-bottom: 18px;
    }

    .title-wrap h1 {
      margin: 0;
      font-size: 1.45rem;
      letter-spacing: 0.02em;
    }

    .subtitle {
      color: var(--muted);
      margin-top: 6px;
      font-size: 0.92rem;
    }

    .pill {
      border: 1px solid var(--border);
      background: var(--panel);
      border-radius: 999px;
      padding: 8px 12px;
      font-size: 0.84rem;
      color: var(--muted);
      white-space: nowrap;
    }

    .grid {
      display: grid;
      grid-template-columns: repeat(4, minmax(0, 1fr));
      gap: 14px;
      margin-bottom: 14px;
    }

    .card {
      background: linear-gradient(145deg, var(--panel) 10%, var(--panel-2) 100%);
      border: 1px solid var(--border);
      border-radius: 14px;
      padding: 14px;
      box-shadow: 0 6px 16px rgba(0, 0, 0, 0.25);
    }

    .label {
      color: var(--muted);
      font-size: 0.8rem;
      text-transform: uppercase;
      letter-spacing: 0.08em;
      margin-bottom: 8px;
    }

    .value {
      font-size: 1.08rem;
      font-weight: 650;
      line-height: 1.25;
      word-break: break-word;
    }

    .value.large {
      font-size: 1.42rem;
    }

    .status-live { color: var(--ok); }
    .status-error, .risk-high { color: var(--danger); }
    .risk-medium { color: var(--warn); }
    .risk-low { color: var(--ok); }

    .alert-box {
      margin-top: 14px;
      border-radius: 12px;
      padding: 12px 14px;
      border: 1px solid;
      background: rgba(255, 255, 255, 0.02);
      font-size: 0.95rem;
    }

    .alert-ok {
      border-color: rgba(31, 212, 121, 0.45);
      color: #bbf8da;
    }

    .alert-warn {
      border-color: rgba(244, 183, 64, 0.45);
      color: #ffe8b3;
    }

    .alert-danger {
      border-color: rgba(255, 93, 93, 0.5);
      color: #ffc8c8;
    }

    .chart-card {
      margin-top: 14px;
    }

    canvas {
      width: 100% !important;
      height: 300px !important;
    }

    @media (max-width: 980px) {
      .grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }
    }

    @media (max-width: 640px) {
      .header { flex-direction: column; align-items: flex-start; }
      .grid { grid-template-columns: 1fr; }
    }
  </style>
</head>
<body>
  <div class=\"container\">
    <div class=\"header\">
      <div class=\"title-wrap\">
        <h1>🏭 IAiOS Industrial Monitoring Console</h1>
        <div class=\"subtitle\">SCADA-style live telemetry and AI decision stream</div>
      </div>
      <div class=\"pill\" id=\"lastUpdate\">Last update: --</div>
    </div>

    <div class=\"grid\">
      <div class=\"card\">
        <div class=\"label\">System Status</div>
        <div id=\"statusValue\" class=\"value large\">--</div>
      </div>
      <div class=\"card\">
        <div class=\"label\">Risk Level</div>
        <div id=\"riskValue\" class=\"value large\">--</div>
      </div>
      <div class=\"card\">
        <div class=\"label\">Alert</div>
        <div id=\"alertValue\" class=\"value\">--</div>
      </div>
      <div class=\"card\">
        <div class=\"label\">AI Decision</div>
        <div id=\"decisionValue\" class=\"value\">--</div>
      </div>
    </div>

    <div id=\"alertBox\" class=\"alert-box alert-ok\">Waiting for live data...</div>

    <div class=\"card chart-card\">
      <div class=\"label\">Risk Trend (Live)</div>
      <canvas id=\"riskChart\"></canvas>
    </div>
  </div>

  <script>
    const LIVE_ENDPOINT = 'https://iaios.onrender.com/live';
    const trendLabels = [];
    const trendValues = [];

    const statusValue = document.getElementById('statusValue');
    const riskValue = document.getElementById('riskValue');
    const alertValue = document.getElementById('alertValue');
    const decisionValue = document.getElementById('decisionValue');
    const alertBox = document.getElementById('alertBox');
    const lastUpdate = document.getElementById('lastUpdate');

    const chart = new Chart(document.getElementById('riskChart'), {
      type: 'line',
      data: {
        labels: trendLabels,
        datasets: [{
          label: 'Failure Risk',
          data: trendValues,
          borderColor: '#3aa0ff',
          backgroundColor: 'rgba(58,160,255,0.2)',
          tension: 0.3,
          fill: true,
          pointRadius: 2
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { labels: { color: '#d9e3ed' } }
        },
        scales: {
          x: {
            ticks: { color: '#92a0af' },
            grid: { color: 'rgba(146,160,175,0.15)' }
          },
          y: {
            min: 0,
            max: 1,
            ticks: { color: '#92a0af' },
            grid: { color: 'rgba(146,160,175,0.15)' }
          }
        }
      }
    });

    function classifyRisk(value) {
      if (value >= 0.7) return { label: 'HIGH', className: 'risk-high', alertClass: 'alert-danger' };
      if (value >= 0.4) return { label: 'MEDIUM', className: 'risk-medium', alertClass: 'alert-warn' };
      return { label: 'LOW', className: 'risk-low', alertClass: 'alert-ok' };
    }

    function setErrorState(message) {
      statusValue.textContent = 'ERROR';
      statusValue.className = 'value large status-error';
      riskValue.textContent = '--';
      riskValue.className = 'value large';
      alertValue.textContent = 'Communication Failure';
      decisionValue.textContent = 'No decision available';
      alertBox.textContent = message;
      alertBox.className = 'alert-box alert-danger';
    }

    async function fetchLiveData() {
      try {
        const response = await fetch(LIVE_ENDPOINT, { cache: 'no-store' });
        if (!response.ok) {
          throw new Error(`HTTP ${response.status}`);
        }

        const data = await response.json();
        const status = (data.status || 'unknown').toString();
        const riskRaw = Number(data?.risk?.failure_risk ?? data?.risk ?? 0);
        const safeRisk = Number.isFinite(riskRaw) ? Math.max(0, Math.min(1, riskRaw)) : 0;
        const riskMeta = classifyRisk(safeRisk);

        statusValue.textContent = status.toUpperCase();
        statusValue.className = `value large ${status === 'live' ? 'status-live' : 'status-error'}`;

        riskValue.textContent = `${riskMeta.label} (${safeRisk.toFixed(2)})`;
        riskValue.className = `value large ${riskMeta.className}`;

        const alertText = safeRisk >= 0.7
          ? 'Critical condition detected. Immediate intervention required.'
          : safeRisk >= 0.4
          ? 'Degradation trend detected. Schedule preventative maintenance.'
          : 'Operations stable. No immediate anomaly action needed.';

        alertValue.textContent = alertText;
        decisionValue.textContent = data.decision || 'No AI decision available';

        alertBox.textContent = `${status.toUpperCase()} | ${alertText}`;
        alertBox.className = `alert-box ${riskMeta.alertClass}`;

        const now = new Date();
        const timestamp = now.toLocaleTimeString();
        lastUpdate.textContent = `Last update: ${timestamp}`;

        trendLabels.push(timestamp);
        trendValues.push(safeRisk);
        if (trendLabels.length > 30) {
          trendLabels.shift();
          trendValues.shift();
        }
        chart.update();
      } catch (error) {
        setErrorState(`Data fetch failed: ${error.message}`);
      }
    }

    fetchLiveData();
    setInterval(fetchLiveData, 5000);
  </script>
</body>
</html>
    """
    return HTMLResponse(content=html)
