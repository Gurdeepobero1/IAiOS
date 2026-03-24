import pandas as pd

def predict_failure():
    df = pd.read_csv("factory_data.csv")

    latest = df.iloc[-1]

    risk = 0

    # Risk logic (can be improved later with ML)
    if latest["temperature"] > 80:
        risk += 0.4

    if latest["pressure"] > 35:
        risk += 0.3

    if latest["vibration"] > 6:
        risk += 0.3

    return {
        "temperature": latest["temperature"],
        "pressure": latest["pressure"],
        "vibration": latest["vibration"],
        "failure_risk": round(risk, 2)
    }


if __name__ == "__main__":
    result = predict_failure()

    print("⚠️ Failure Risk Analysis:\n")
    for k, v in result.items():
        print(f"{k}: {v}")
        