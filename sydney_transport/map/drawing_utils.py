import pygame
from math import sqrt

Point = tuple[int, int]

def extract_stops(filename: str) -> list:
    with open(filename, "r") as f:
        return f.readlines()

def increment_line_hex_colour(old_hex) -> str:
    hex_code = old_hex[1:]
    red, green, _ = [hex_code[i:i + 2] for i in range(0, len(hex_code), 2)]

    red_decimal_val = int(red, 16)
    green_decimal_val = int(green, 16)
    new_red_hex = "FF"
    new_green_hex = "00"

    # increasing red
    if red_decimal_val < 255:
        new_red_hex = f"{red_decimal_val + 1:02X}".upper()
        new_green_hex = "FF"
    # decreasing green
    elif green_decimal_val > 0:
        new_red_hex = "FF"
        new_green_hex = f"{green_decimal_val - 1:02X}".upper()

    return f"#{new_red_hex}{new_green_hex}00"

def calculate_distance_hex_colour(point: Point, end_point: Point, largest_distance: float, scale: float) -> str:
    distance = get_distance_between_points(end_point, point, scale)
    total_hex_value = int(distance / (largest_distance / 510)) # red + green value

    # distance of point to end_point is more than half the largest_distance
    # coloured yellow-red
    if total_hex_value > 255:
        red_decimal_val = 255
        green_decimal_val = 255 - (255 - total_hex_value)
    # coloured green-yellow
    else:
        green_decimal_val = 255
        red_decimal_val = 255 + (255 - total_hex_value)

    # check values in range 0, 255
    red_decimal_val = max(0, min(255, red_decimal_val))
    green_decimal_val = max(0, min(255, green_decimal_val))

    new_red_hex = f"{red_decimal_val:02X}".upper()
    new_green_hex = f"{green_decimal_val:02X}".upper()

    return f"#{new_red_hex}{new_green_hex}00"

def get_distance_between_points(start: Point, end: Point, scale: float) -> float:
    y1, x1 = int(start[0] * scale), int(start[1] * scale)
    y2, x2 = int(end[0] * scale), int(end[1] * scale)

    return sqrt((x2 - x1)**2 + (y2 - y1)**2)

def get_furthest_distance_from_point(point: Point, scale: float) -> float:
    furthest_corner_point = get_corner_with_furthest_distance(point, scale)
    return get_distance_between_points(point, furthest_corner_point, scale)

def get_corner_with_furthest_distance(point: Point, scale: float) -> tuple[int, int]:
    y, x = point

    min_y, min_x = 0, 0
    middle_y, middle_x = int(2160 * scale), int(3240 * scale),
    max_y, max_x = int(4320 * scale), int(6480 * scale)

    # first quadrant
    if x > middle_x and y <= middle_y:
        return max_y, min_x
    # second quadrant
    if x <= middle_x and y <= middle_y:
        return max_y, max_x
    # third quadrant
    if x <= middle_x and y > middle_y:
        return min_y, max_x
    # fourth quadrant
    if x > middle_x and y > middle_y:
        return min_y, min_x

    return min_y, min_x

def coordinates_to_pixels(lat: float, lon: float) -> Point:
    y = int(-5416.61765 * float(lat) - 181400.485)
    x = int(4479.38462 * float(lon) - 672890.965)
    return y, x

def draw_line(surface: pygame.Surface, scale: float, colour: str,
              start: Point, end: Point, width: int) -> None:
    start_y, start_x = start
    end_y, end_x = end
    pygame.draw.line(
        surface,
        colour,
        (start_x * scale, start_y * scale),
        (end_x * scale, end_y * scale),
        width
    )
