import json

class MetricSelector:
    @staticmethod
    def get_metrics_for_category(category):
        # Load from metrics_map.json
        with open("data/metrics_map.json", "r") as f:
            mapping = json.load(f)
        return mapping.get(category.lower(), {})
