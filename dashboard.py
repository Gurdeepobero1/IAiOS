import streamlit as st
import requests
import pandas as pd

st.set_page_config(page_title="1OS", layout="wide")

st.title("🏭 1OS - Industrial AI OS")

API_URL = "https://your-render-url.onrender.com/live"

def fetch_data():
    try:
        res = requests.get(API_URL, timeout=10)
        return res.json()
    except:
        return {"status": "error"}

data = fetch_data()

if data["status"] == "live":

    col1, col2 = st.columns(2)

    # Risk
    with col1:
        st.subheader("⚠️ Risk Level")
        risk = data["risk"]["failure_risk"]

        if risk > 0.7:
            st.error(f"HIGH RISK: {risk}")
        elif risk > 0.4:
            st.warning(f"MEDIUM RISK: {risk}")
        else:
            st.success(f"SAFE: {risk}")

    # Decision
    with col2:
        st.subheader("🧠 AI Decision")
        st.write(data["decision"])

    # Graph
    st.subheader("📊 Sensor Data")

    try:
        df = pd.read_csv("live_data.csv").tail(100)
        st.line_chart(df)
    except:
        st.warning("No live data available")

else:
    st.warning("System not live")