def get_distance_score(distance_m):
    if distance_m < 200:
        return 1.0
    elif distance_m < 500:
        return 0.8
    elif distance_m < 1000:
        return 0.5
    else:
        return 0.2
