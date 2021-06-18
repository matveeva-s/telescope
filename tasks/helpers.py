def converting_degrees(value):
    degrees = abs(int(value))
    minutes = abs(value - degrees) * 60
    seconds = int(abs(minutes - int(minutes)) * 60)
    minutes = int(minutes)
    return degrees, minutes, seconds


def is_float(value):
    try:
        float(value)
        return True
    except ValueError:
        return False


def is_int(value):
    try:
        int(value)
        return True
    except ValueError:
        return False
