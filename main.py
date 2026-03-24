from fastapi import FastAPI
import pandas as pd
import os

from anomaly import detect_anomalies
from predictor import predict_failure
from decision_ai import generate_decision
from machines import machines

app = FastAPI(title="Industrial AI Backbone")


@app.get("/")
def home():
    return {"message": "IAOS is running 🚀"}


# 🔹 BASIC RUN (STATIC DATA)
@app.get("/run")
def run_system():
    try:
        df = pd.read_csv("factory_data.csv")

        anomalies = detect_anomalies()
        risk = predict_failure()

        decision = generate_decision(df.tail(5), risk)

        return {
            "status": "success",
            "risk": risk,
            "decision": decision
        }

    except Exception as e:
        return {"status": "error", "message": str(e)}


# 🔹 LIVE SYSTEM
@app.get("/live")
def live_system():
    try:
        if not os.path.exists("live_data.csv"):
            return {"status": "waiting", "message": "Live data not started"}

        df = pd.read_csv("live_data.csv").tail(50)

        anomalies = detect_anomalies()
        risk = predict_failure()

        decision = generate_decision(df.tail(5), risk)

        return {
            "status": "live",
            "risk": risk,
            "decision": decision
        }

    except Exception as e:
        return {"status": "error", "message": str(e)}


# 🔹 MULTI-MACHINE
@app.get("/machine/{machine_id}")
def run_machine(machine_id: str):
    try:
        file = machines.get(machine_id)

        if not file:
            return {"error": "Machine not found"}

        df = pd.read_csv(file)

        anomalies = detect_anomalies()
        risk = predict_failure()

        decision = generate_decision(df.tail(5), risk)

        return {
            "machine": machine_id,
            "risk": risk,
            "decision": decision
        }

    except Exception as e:
        return {"error": str(e)}
import os

port = int(os.environ.get("PORT", 10000))