from metrics.traffic.traffic_school_business_proximity.distance_weighting import get_distance_score

class SchoolBusinessMetric:
    def __init__(self, location):
        self.location = location

    def calculate(self):
        school_distance = 350
        business_distance = 600
        school_score = get_distance_score(school_distance)
        business_score = get_distance_score(business_distance)
        return round(0.5 * school_score + 0.5 * business_score, 2)
