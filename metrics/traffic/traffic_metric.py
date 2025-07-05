from metrics.traffic.traffic_population_density.population_density_metric import PopulationDensityMetric
from metrics.traffic.traffic_school_business_proximity.school_business_metric import SchoolBusinessMetric

class TrafficMetric:
    def __init__(self, location):
        self.location = location

    def calculate(self):
        pop_score = PopulationDensityMetric(self.location).calculate()
        sb_score = SchoolBusinessMetric(self.location).calculate()
        return round(0.4 * pop_score + 0.6 * sb_score, 2)
