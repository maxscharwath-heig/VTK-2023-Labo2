# VTK - Labo 2
# Nicolas Crausaz & Maxime Scharwath
# Define helpers functions

import math

def spherical_to_cartesian(radius: float, latitude: float, longitude: float):
    '''
    Convert spherical coordinates to cartesian coordinates
    :param radius: Radius of the sphere
    :param latitude: Latitude in degrees
    :param longitude: Longitude in degrees
    :return: x, y, z coordinates
    '''

    radians = [math.radians(latitude), math.radians(longitude)]

    x = radius * math.sin(radians[0]) * math.sin(radians[1])
    y = radius * math.cos(radians[0])
    z = radius * math.sin(radians[0]) * math.cos(radians[1])
    return x, y, z