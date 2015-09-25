import os
import math

import pygame

from .vector2 import Vector2

MEDIA_PATH = os.path.join(os.path.dirname(__file__), 'media')


def blend_color(color1, color2, blend_ratio):
    """
    Blend two colors together given the blend_ration

    :param color1: pygame.Color
    :param color2: pygame.Color
    :param blend_ratio: float between 0.0 and 1.0
    :return: pygame.Color
    """
    r = color1.r + (color2.r - color1.r) * blend_ratio
    g = color1.g + (color2.g - color1.g) * blend_ratio
    b = color1.b + (color2.b - color1.b) * blend_ratio
    a = color1.a + (color2.a - color1.a) * blend_ratio
    return pygame.Color(int(r), int(g), int(b), int(a))


def vector2_to_floor(v2):
    """
    call math.floor on Vector2.x and Vector.y
    :param v2: pygame.math.Vector2
    :return: A new Vector2 with the x, y values math.floor
    """

    return Vector2(math.floor(v2.x), math.floor(v2.y))


def vector2_to_int(v2):
    """
    call int on Vector2.x and Vector.y
    :param v2: pygame.math.Vector2
    :return: A (x, y) integer tuple
    """

    return int(v2.x), int(v2.y)
