import pandas as pd
import numpy as np
import time

def stream_data():
    np.random.seed()

    while True:
        data = {
            "temperature": 70 + np.random.normal(0, 2),
            "pressure": 30 + np.random.normal(0, 1),
            "vibration": 5 + np.random.normal(0, 0.5)
        }

        df = pd.DataFrame([data])
        df.to_csv("live_data.csv", mode='a', header=False, index=False)

        print("Streaming:", data)
        time.sleep(1)


if __name__ == "__main__":
    # create file with header first
    df = pd.DataFrame(columns=["temperature", "pressure", "vibration"])
    df.to_csv("live_data.csv", index=False)

    stream_data()