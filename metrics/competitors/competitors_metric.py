class CompetitorsMetric:
    def __init__(self, location):
        self.location = location

    def calculate(self):
        competitor_count = 5
        if competitor_count == 0:
            return 1.0
        elif competitor_count < 3:
            return 0.8
        elif competitor_count < 7:
            return 0.5
        else:
            return 0.2
