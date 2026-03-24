import pandas as pd
import numpy as np

def generate_data():
    np.random.seed(42)

    time = pd.date_range(start="2024-01-01", periods=500, freq="min")

    temperature = 70 + np.random.normal(0, 2, 500)
    pressure = 30 + np.random.normal(0, 1, 500)
    vibration = 5 + np.random.normal(0, 0.5, 500)

    # Inject anomaly (simulating machine issue)
    temperature[300:320] += 15
    pressure[300:320] += 5

    df = pd.DataFrame({
        "time": time,
        "temperature": temperature,
        "pressure": pressure,
        "vibration": vibration
    })

    df.to_csv("factory_data.csv", index=False)
    print("✅ Data generated: factory_data.csv")

if __name__ == "__main__":
    generate_data()