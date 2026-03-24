import time
import requests
import streamlit as st

API_URL = "https://iaios.onrender.com/live"
REFRESH_SECONDS = 5
MAX_POINTS = 30

st.set_page_config(page_title="IAiOS Monitor", layout="wide")
st.title("🏭 IAiOS Live Monitor")

if "risk_history" not in st.session_state:
    st.session_state.risk_history = []
if "time_history" not in st.session_state:
    st.session_state.time_history = []


def classify_risk(risk_value: float) -> str:
    if risk_value >= 0.7:
        return "HIGH"
    if risk_value >= 0.4:
        return "MEDIUM"
    return "LOW"


def risk_color(level: str) -> str:
    return {"LOW": "🟢", "MEDIUM": "🟡", "HIGH": "🔴"}.get(level, "⚪")


def fetch_live_data() -> dict:
    try:
        response = requests.get(API_URL, timeout=8)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as exc:
        return {"status": "error", "message": str(exc)}


data = fetch_live_data()
status = str(data.get("status", "unknown"))

risk_raw = data.get("risk", 0)
if isinstance(risk_raw, dict):
    risk_value = float(risk_raw.get("failure_risk", 0) or 0)
else:
    try:
        risk_value = float(risk_raw)
    except (TypeError, ValueError):
        risk_value = 0.0

risk_value = max(0.0, min(1.0, risk_value))
risk_level = classify_risk(risk_value)
alert_text = (
    "Critical condition detected"
    if risk_level == "HIGH"
    else "Preventive maintenance recommended"
    if risk_level == "MEDIUM"
    else "System stable"
)

decision = data.get("decision", "No decision available")

col1, col2, col3, col4 = st.columns(4)
col1.metric("Status", status.upper())
col2.metric("Risk", f"{risk_color(risk_level)} {risk_level} ({risk_value:.2f})")
col3.metric("Alert", alert_text)
col4.metric("AI Decision", str(decision)[:80])

if status == "error":
    st.error(f"Data fetch failed: {data.get('message', 'Unknown error')}")
elif risk_level == "HIGH":
    st.error(alert_text)
elif risk_level == "MEDIUM":
    st.warning(alert_text)
else:
    st.success(alert_text)

now_label = time.strftime("%H:%M:%S")
st.session_state.time_history.append(now_label)
st.session_state.risk_history.append(risk_value)

if len(st.session_state.risk_history) > MAX_POINTS:
    st.session_state.risk_history = st.session_state.risk_history[-MAX_POINTS:]
    st.session_state.time_history = st.session_state.time_history[-MAX_POINTS:]

st.subheader("Risk Trend")
st.line_chart(
    {
        "time": st.session_state.time_history,
        "risk": st.session_state.risk_history,
    },
    x="time",
    y="risk",
)

st.caption(f"Auto-refreshing every {REFRESH_SECONDS} seconds")
time.sleep(REFRESH_SECONDS)
st.rerun()
