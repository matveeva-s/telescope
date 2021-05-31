def converting_degrees(value):
    degrees = abs(int(value))
    minutes = abs(value - degrees) * 60
    seconds = int(abs(minutes - int(minutes)) * 60)
    minutes = int(minutes)
    return degrees, minutes, seconds
