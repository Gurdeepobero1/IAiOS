import pandas as pd
from sklearn.ensemble import IsolationForest

def detect_anomalies():
    # Load data
    df = pd.read_csv("factory_data.csv")

    # Select relevant features
    features = df[["temperature", "pressure", "vibration"]]

    # Train model
    model = IsolationForest(contamination=0.05, random_state=42)
    df["anomaly"] = model.fit_predict(features)

    # Filter anomalies (-1 means anomaly)
    anomalies = df[df["anomaly"] == -1]

    return anomalies.tail(10)


if __name__ == "__main__":
    anomalies = detect_anomalies()
    print("🚨 Detected Anomalies:\n")
    print(anomalies)