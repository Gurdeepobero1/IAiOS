import requests
from knowledge_graph import KnowledgeGraph

SARVAM_API_KEY = "sk_ih6226yx_DYMpLhzSWUFdvb3I7aypIoNi"

kg = KnowledgeGraph()

def generate_decision(data_df, risk):
    # Ensure it's a DataFrame
    latest = data_df.iloc[-1].to_dict()

    # Knowledge graph insights
    kg_insights = kg.analyze(latest)

    url = "https://api.sarvam.ai/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {SARVAM_API_KEY}",
        "Content-Type": "application/json"
    }

    prompt = f"""
    You are an industrial AI system.

    Machine Data:
    {data_df.tail(5).to_string()}

    Risk:
    {risk}

    Domain Insights:
    {kg_insights}

    Give:
    Problem:
    Cause:
    Recommended Action:
    """

    payload = {
        "model": "sarvam-m",
        "messages": [{"role": "user", "content": prompt}]
    }

    response = requests.post(url, headers=headers, json=payload)

    if response.status_code == 200:
        return response.json()["choices"][0]["message"]["content"]
    else:
        return f"Error: {response.text}"