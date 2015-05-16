import math

# Calculate distance between two points using pythagoras
def calculate_distance(point1, point2):
    legx = (point1[0] - point2[0]) ** 2
    legy = (point1[1] - point2[1]) ** 2
    return math.sqrt(legx + legy)
