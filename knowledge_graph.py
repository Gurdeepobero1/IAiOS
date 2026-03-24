class KnowledgeGraph:
    def __init__(self):
        self.graph = {
            "temperature": {
                "affects": ["efficiency", "energy_cost"],
                "high": "Overheating reduces efficiency and increases cost",
                "low": "Low temperature reduces production output"
            },
            "pressure": {
                "affects": ["flow_rate", "system_stability"],
                "high": "High pressure may damage valves",
                "low": "Low pressure reduces flow efficiency"
            },
            "vibration": {
                "affects": ["machine_health"],
                "high": "High vibration indicates mechanical wear",
                "low": "Normal operation"
            }
        }

    def analyze(self, data):
        insights = []

        for key in ["temperature", "pressure", "vibration"]:
            value = data[key]

            if key == "temperature" and value > 80:
                insights.append(self.graph[key]["high"])

            elif key == "pressure" and value > 35:
                insights.append(self.graph[key]["high"])

            elif key == "vibration" and value > 6:
                insights.append(self.graph[key]["high"])

        return insights