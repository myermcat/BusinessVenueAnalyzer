class Scorer:
    @staticmethod
    def score(metric_tuples):
        # metric_tuples = [(metric, value, weight), ...]
        total = 0
        breakdown = {}
        for metric, value, weight in metric_tuples:
            weighted = value * weight
            breakdown[metric] = {"value": value, "weight": weight, "weighted": weighted}
            total += weighted
        return total, breakdown
