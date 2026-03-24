import streamlit as st
import requests
import pandas as pd

st.set_page_config(page_title="Industrial AI OS", layout="wide")

st.title("🏭 Industrial AI Operating System")

# Auto refresh toggle
auto_refresh = st.checkbox("Auto Refresh (Live Mode)")

def fetch_data():
    res = requests.get("https://your-render-url.onrender.com/live")
    return res.json()

data = fetch_data()

if data["status"] == "live":

    col1, col2 = st.columns(2)

    # 🔴 RISK METER
    with col1:
        st.subheader("⚠️ Failure Risk")
        risk = data["risk"]["failure_risk"]

        if risk > 0.7:
            st.error(f"🔴 HIGH RISK: {risk}")
        elif risk > 0.4:
            st.warning(f"🟡 MEDIUM RISK: {risk}")
        else:
            st.success(f"🟢 SAFE: {risk}")

    # 🧠 AI DECISION
    with col2:
        st.subheader("🧠 AI Decision")
        st.write(data["decision"])

    # 📊 LIVE DATA GRAPH
    st.subheader("📊 Live Sensor Data")

    try:
        df = pd.read_csv("live_data.csv").tail(100)
        st.line_chart(df)
    except:
        st.warning("Waiting for live data...")

else:
    st.warning("System waiting for live data...")

# 🔁 Auto refresh
if auto_refresh:
    st.rerun()