def validate_location(location):
    # For now, we just check it's a non-empty string
    return isinstance(location, str) and len(location.strip()) > 0
