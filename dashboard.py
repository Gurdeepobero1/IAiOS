from datetime import datetime
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import streamlit as st

API_URL = "https://iaios.onrender.com/live"
CONNECT_TIMEOUT = 10
READ_TIMEOUT = 45
MAX_POINTS = 60

st.set_page_config(page_title="IAiOS SCADA Console", layout="wide")

st.markdown(
    """
    <style>
      .stApp {
        background: radial-gradient(circle at 85% 0%, #1c2d42 0%, #0d131c 45%);
        color: #e9eef6;
      }
      .main-title {
        font-size: 2rem;
        font-weight: 800;
        margin-bottom: .15rem;
      }
      .subtitle {
        color: #9db2c8;
        margin-bottom: 1.1rem;
      }
      .status-chip {
        display: inline-block;
        border-radius: 999px;
        border: 1px solid #30435b;
        color: #b4c6d9;
        padding: .35rem .7rem;
        font-size: .8rem;
        margin-bottom: 1rem;
      }
      .scada-card {
        background: linear-gradient(145deg, #101a27 0%, #1a2738 100%);
        border: 1px solid #2e4159;
        border-radius: 14px;
        padding: 16px;
        box-shadow: 0 8px 20px rgba(0,0,0,.28);
        min-height: 122px;
      }
      .card-label {
        color: #8ea4bc;
        font-size: .78rem;
        letter-spacing: .08em;
        text-transform: uppercase;
        margin-bottom: 8px;
      }
      .card-value {
        color: #f3f8ff;
        font-size: 1.18rem;
        font-weight: 700;
        line-height: 1.35;
      }
      .hint-box {
        border: 1px dashed #3a5270;
        background: rgba(58, 82, 112, 0.18);
        border-radius: 12px;
        padding: .75rem .9rem;
        color: #c5d4e2;
        margin-top: 1rem;
      }
    </style>
    """,
    unsafe_allow_html=True,
)

if "risk_history" not in st.session_state:
    st.session_state.risk_history = []
if "time_history" not in st.session_state:
    st.session_state.time_history = []
if "last_data" not in st.session_state:
    st.session_state.last_data = None
if "last_error" not in st.session_state:
    st.session_state.last_error = ""
if "last_fetch_time" not in st.session_state:
    st.session_state.last_fetch_time = "--"


def classify_risk(risk_value: float) -> str:
    if risk_value >= 0.7:
        return "HIGH"
    if risk_value >= 0.4:
        return "MEDIUM"
    return "LOW"


def risk_color(level: str) -> str:
    return {"LOW": "#27d07d", "MEDIUM": "#f4b740", "HIGH": "#ff6a6a"}.get(level, "#9cb0c5")


def build_session() -> requests.Session:
    session = requests.Session()
    retries = Retry(
        total=4,
        connect=4,
        read=4,
        backoff_factor=1.0,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET"],
    )
    adapter = HTTPAdapter(max_retries=retries)
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    return session


def fetch_live_data() -> dict:
    try:
        with build_session() as session:
            response = session.get(API_URL, timeout=(CONNECT_TIMEOUT, READ_TIMEOUT))
            response.raise_for_status()
            payload = response.json()
            payload["_fetched_at"] = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
            return payload
    except requests.RequestException as exc:
        return {"status": "error", "message": str(exc)}


def extract_risk(data: dict) -> float:
    risk_raw = data.get("risk", 0)
    if isinstance(risk_raw, dict):
        value = risk_raw.get("failure_risk", 0)
    else:
        value = risk_raw
    try:
        return max(0.0, min(1.0, float(value)))
    except (TypeError, ValueError):
        return 0.0


def add_history_point(risk_value: float) -> None:
    now = datetime.utcnow().strftime("%H:%M:%S")
    st.session_state.time_history.append(now)
    st.session_state.risk_history.append(risk_value)
    if len(st.session_state.risk_history) > MAX_POINTS:
        st.session_state.risk_history = st.session_state.risk_history[-MAX_POINTS:]
        st.session_state.time_history = st.session_state.time_history[-MAX_POINTS:]


st.markdown("<div class='main-title'>🏭 IAiOS Industrial SCADA Console</div>", unsafe_allow_html=True)
st.markdown("<div class='subtitle'>Manual refresh dashboard with resilient Render-to-Streamlit connectivity.</div>", unsafe_allow_html=True)
st.markdown(f"<div class='status-chip'>Endpoint: {API_URL}</div>", unsafe_allow_html=True)

left, right = st.columns([1, 1])
with left:
    refresh = st.button("🔄 Fetch Latest from Render", type="primary", use_container_width=True)
with right:
    clear_chart = st.button("🧹 Clear Trend History", use_container_width=True)

if clear_chart:
    st.session_state.risk_history = []
    st.session_state.time_history = []

if refresh or st.session_state.last_data is None:
    incoming = fetch_live_data()
    if incoming.get("status") != "error":
        st.session_state.last_data = incoming
        st.session_state.last_error = ""
        st.session_state.last_fetch_time = incoming.get("_fetched_at", "--")
        add_history_point(extract_risk(incoming))
    else:
        st.session_state.last_error = incoming.get("message", "Unknown connection error")

data = st.session_state.last_data or {"status": "error", "message": "No data loaded yet"}
status = str(data.get("status", "unknown")).upper()
risk_value = extract_risk(data)
risk_level = classify_risk(risk_value)
decision = str(data.get("decision", "No AI decision available"))

alert_text = (
    "Critical condition detected. Immediate intervention required."
    if risk_level == "HIGH"
    else "Degradation trend detected. Preventive maintenance advised."
    if risk_level == "MEDIUM"
    else "Operations stable. No immediate action needed."
)

c1, c2, c3, c4 = st.columns(4)
c1.markdown(
    f"<div class='scada-card'><div class='card-label'>System Status</div><div class='card-value'>{status}</div></div>",
    unsafe_allow_html=True,
)
c2.markdown(
    f"<div class='scada-card'><div class='card-label'>Risk</div><div class='card-value' style='color:{risk_color(risk_level)}'>{risk_level} ({risk_value:.2f})</div></div>",
    unsafe_allow_html=True,
)
c3.markdown(
    f"<div class='scada-card'><div class='card-label'>Alert</div><div class='card-value' style='font-size:1rem'>{alert_text}</div></div>",
    unsafe_allow_html=True,
)
c4.markdown(
    f"<div class='scada-card'><div class='card-label'>AI Decision</div><div class='card-value' style='font-size:1rem'>{decision[:180]}</div></div>",
    unsafe_allow_html=True,
)

st.markdown("### Failure Risk Gauge")
st.progress(risk_value)

if st.session_state.last_error:
    st.error(
        "Unable to fetch latest data from Render right now. "
        f"Showing last successful snapshot from {st.session_state.last_fetch_time}. "
        f"Error: {st.session_state.last_error}"
    )

st.markdown("### Risk Trend")
if st.session_state.risk_history:
    st.line_chart(
        {"time": st.session_state.time_history, "risk": st.session_state.risk_history},
        x="time",
        y="risk",
    )
else:
    st.info("No trend points yet. Click 'Fetch Latest from Render' to load data.")

st.markdown(
    f"<div class='hint-box'>Last successful data pull: {st.session_state.last_fetch_time}. "
    "Auto-refresh is disabled as requested.</div>",
    unsafe_allow_html=True,
)
