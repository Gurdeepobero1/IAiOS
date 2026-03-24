from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import requests

app = FastAPI()

BACKEND_URL = "https://iaios.onrender.com/live"

@app.get("/", response_class=HTMLResponse)
def dashboard():
    try:
        res = requests.get(BACKEND_URL)
        data = res.json()
    except:
        data = {"status": "error"}

    html = f"""
    <html>
    <head>
        <title>1OS Dashboard</title>
    </head>
    <body style="font-family: Arial; padding: 20px;">
        <h1>🏭 1OS - Industrial AI OS</h1>

        <h2>Status: {data.get("status")}</h2>

        <h3>Risk:</h3>
        <p>{data.get("risk")}</p>

        <h3>Decision:</h3>
        <p>{data.get("decision")}</p>
    </body>
    </html>
    """

    return html