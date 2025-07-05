from engine.metric_selector import MetricSelector
from engine.single_metric_calculator import SingleMetricCalculator
from engine.scorer import Scorer
from engine.result_formatter import ResultFormatter
from engine.location_validator import validate_location

def main():
    category = input("Enter your business category: ")
    location = input("Enter your location (address or coordinates): ")
    
    if not validate_location(location):
        print("Invalid location.")
        return

    metrics_with_weights = MetricSelector.get_metrics_for_category(category)
    
    raw_scores = []
    for metric, weight in metrics_with_weights.items():
        value = SingleMetricCalculator.calculate(metric, location)
        raw_scores.append((metric, value, weight))

    final_score, breakdown = Scorer.score(raw_scores)
    
    result = ResultFormatter.format(final_score, breakdown)
    print(result)

if __name__ == "__main__":
    main()
