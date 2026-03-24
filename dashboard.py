from datetime import datetime
import time
import requests
import streamlit as st

API_URL = "https://iaios.onrender.com/live"
REQUEST_TIMEOUT = 20
REFRESH_SECONDS = 5
MAX_POINTS = 50

st.set_page_config(page_title="IAiOS SCADA Console", layout="wide")

st.markdown(
    """
    <style>
      .stApp {
        background: radial-gradient(circle at top right, #17212f 0%, #0d131c 45%);
        color: #e9eef6;
      }
      .main-title {
        font-size: 2rem;
        font-weight: 700;
        margin-bottom: 0.2rem;
      }
      .subtitle {
        color: #93a4b8;
        margin-bottom: 1rem;
      }
      .scada-card {
        background: linear-gradient(140deg, #121b27 0%, #1a2534 100%);
        border: 1px solid #2a3a50;
        border-radius: 14px;
        padding: 16px;
        box-shadow: 0 6px 18px rgba(0,0,0,.28);
        min-height: 110px;
      }
      .card-label {
        color: #93a4b8;
        font-size: 0.78rem;
        letter-spacing: .08em;
        text-transform: uppercase;
        margin-bottom: 10px;
      }
      .card-value {
        font-size: 1.2rem;
        font-weight: 700;
        color: #f4f8fd;
      }
      .chip {
        display: inline-block;
        padding: 6px 10px;
        border-radius: 999px;
        font-size: 0.8rem;
        border: 1px solid #2a3a50;
        color: #9cb0c5;
      }
    </style>
    """,
    unsafe_allow_html=True,
)

# Session state
if "risk_history" not in st.session_state:
    st.session_state.risk_history = []
if "time_history" not in st.session_state:
    st.session_state.time_history = []
if "last_data" not in st.session_state:
    st.session_state.last_data = None
if "last_error" not in st.session_state:
    st.session_state.last_error = ""


def classify_risk(risk_value: float) -> str:
    if risk_value >= 0.7:
        return "HIGH"
    if risk_value >= 0.4:
        return "MEDIUM"
    return "LOW"


def risk_color(level: str) -> str:
    return {"LOW": "#1fd479", "MEDIUM": "#f4b740", "HIGH": "#ff5d5d"}.get(level, "#9cb0c5")


def fetch_live_data() -> dict:
    try:
        response = requests.get(API_URL, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as exc:
        return {"status": "error", "message": str(exc)}


# Title
st.markdown("<div class='main-title'>🏭 IAiOS Industrial SCADA Console</div>", unsafe_allow_html=True)
st.markdown("<div class='subtitle'>Live telemetry, AI decisioning, and risk intelligence.</div>", unsafe_allow_html=True)

# Fetch data
data = fetch_live_data()
status = str(data.get("status", "unknown"))

risk_raw = data.get("risk", 0)
if isinstance(risk_raw, dict):
    risk_value = float(risk_raw.get("failure_risk", 0) or 0)
else:
    try:
        risk_value = float(risk_raw)
    except:
        risk_value = 0.0

risk_value = max(0.0, min(1.0, risk_value))
risk_level = classify_risk(risk_value)

alert_text = (
    "Critical condition detected. Immediate intervention required."
    if risk_level == "HIGH"
    else "Degradation trend detected. Preventive maintenance advised."
    if risk_level == "MEDIUM"
    else "Operations stable."
)

decision = str(data.get("decision", "No decision available"))

# Cards
col1, col2, col3, col4 = st.columns(4)

col1.markdown(f"<div class='scada-card'><div class='card-label'>System Status</div><div class='card-value'>{status.upper()}</div></div>", unsafe_allow_html=True)

col2.markdown(f"<div class='scada-card'><div class='card-label'>Risk</div><div class='card-value' style='color:{risk_color(risk_level)}'>{risk_level} ({risk_value:.2f})</div></div>", unsafe_allow_html=True)

col3.markdown(f"<div class='scada-card'><div class='card-label'>Alert</div><div class='card-value'>{alert_text}</div></div>", unsafe_allow_html=True)

col4.markdown(f"<div class='scada-card'><div class='card-label'>AI Decision</div><div class='card-value'>{decision[:120]}</div></div>", unsafe_allow_html=True)

# Risk bar
st.progress(risk_value)

# History
now = datetime.utcnow().strftime("%H:%M:%S")
st.session_state.time_history.append(now)
st.session_state.risk_history.append(risk_value)

if len(st.session_state.risk_history) > MAX_POINTS:
    st.session_state.risk_history = st.session_state.risk_history[-MAX_POINTS:]
    st.session_state.time_history = st.session_state.time_history[-MAX_POINTS:]

# Chart
st.subheader("📈 Risk Trend")
st.line_chart({
    "time": st.session_state.time_history,
    "risk": st.session_state.risk_history,
})

# Auto refresh
st.caption(f"Auto-refresh every {REFRESH_SECONDS}s")
time.sleep(REFRESH_SECONDS)
st.rerun()
