#  legame/__init__.py
#
#  Copyright 2020 - 2025 Leon Dionne <ldionne@dridesign.sh.cn>
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#
"""
Modules which aid in creating 2-dimensional games with pygame.
"""
import math
from pygame.math import Vector2 as Vector

__version__ = "1.0.0"

PI						= math.pi
HALF_PI					= PI / 2.0
TWO_PI					= PI * 2.0
QUARTER_PI				= PI / 4.0

DEGREES_EAST			= 0.0
DEGREES_SOUTHEAST		= 45.0
DEGREES_SOUTH			= 90.0
DEGREES_SOUTHWEST		= 135.0
DEGREES_WEST			= 180.0
DEGREES_NORTHWEST		= -135.0
DEGREES_NORTH			= -90.0
DEGREES_NORTHEAST		= -45.0

RADIANS_EAST			= 0.0
RADIANS_SOUTHEAST		= QUARTER_PI
RADIANS_SOUTH			= HALF_PI
RADIANS_SOUTHWEST		= HALF_PI + QUARTER_PI
RADIANS_WEST			= PI
RADIANS_NORTHWEST		= -HALF_PI - QUARTER_PI
RADIANS_NORTH			= -HALF_PI
RADIANS_NORTHEAST		= -QUARTER_PI

RADIANS_ZERO			= RADIANS_EAST
RADIANS_45				= RADIANS_SOUTHEAST
RADIANS_90				= RADIANS_SOUTH
RADIANS_135				= RADIANS_SOUTHWEST
RADIANS_180				= RADIANS_WEST
RADIANS_NEG45			= RADIANS_NORTHEAST
RADIANS_NEG90			= RADIANS_NORTH
RADIANS_NEG135			= RADIANS_NORTHWEST

COMPASS_NORTH			= 0
COMPASS_NORTHEAST		= 1
COMPASS_EAST			= 2
COMPASS_SOUTHEAST		= 3
COMPASS_SOUTH			= 4
COMPASS_SOUTHWEST		= 5
COMPASS_WEST			= 6
COMPASS_NORTHWEST		= 7

SIDE_TOP				= COMPASS_NORTH
SIDE_RIGHT				= COMPASS_EAST
SIDE_BOTTOM				= COMPASS_SOUTH
SIDE_LEFT				= COMPASS_WEST

OFFSCREEN_TOP			= 0b1000
OFFSCREEN_BOTTOM		= 0b0100
OFFSCREEN_LEFT			= 0b0010
OFFSCREEN_RIGHT			= 0b0001
OFFSCREEN_TOPLEFT		= 0b1010
OFFSCREEN_TOPRIGHT		= 0b1001
OFFSCREEN_BOTTOMLEFT	= 0b0110
OFFSCREEN_BOTTOMRIGHT	= 0b0101

def deg2vector(degrees, magnitude=1.0):
	vector = Vector()
	vector.from_polar((magnitude, degrees))
	return vector

def rad2vector(radians, magnitude=1.0):
	vector = Vector()
	vector.from_polar((magnitude, math.degrees(radians)))
	return vector

def normal_radians(radians):
	"""
	Returns the radians given clamped to within the range -PI to PI
	"""
	radians = radians % TWO_PI
	if radians < -PI:
		radians += TWO_PI
	elif radians > PI:
		radians -= TWO_PI
	return radians

def turning_degrees(degrees):
	"""
	Clamps the given degrees to within range -180.0 to +180.0.
	"""
	if degrees < -180.0:
		while degrees < -180.0:
			degrees += 360.0
	elif degrees >= 180.0:
		while degrees >= 180.0:
			degrees -= 360.0
	return degrees

def normal_degrees(degrees):
	"""
	Clamps the given degrees to within range 0.0 to +359.999....
	"""
	return degrees % 360

def deg2side(degrees):
	"""
	Returns one of the "SIDE_<direction>" constants.
	"""
	degrees = normal_degrees(degrees)
	if degrees < 135.0:
		if degrees < 45.0:
			return SIDE_RIGHT
		return SIDE_BOTTOM
	if degrees < 225.0:
		return SIDE_LEFT
	if degrees > 315.0:
		return SIDE_RIGHT
	return SIDE_TOP

def rad2side(radians):
	"""
	Returns one of the "SIDE_<direction>" constants.
	"""
	radians = normal_radians(radians)
	if radians < RADIANS_NORTHEAST:
		if radians < RADIANS_NORTHWEST:
			return SIDE_LEFT
		return SIDE_TOP
	if radians > RADIANS_SOUTHEAST:
		if radians > RADIANS_SOUTHWEST:
			return SIDE_LEFT
		return SIDE_BOTTOM
	return SIDE_RIGHT

def deg2compass(degrees):
	"""
	Returns one of the "COMPASS_<direction>" constants.
	"""
	degrees = normal_degrees(degrees)
	if degrees < 157.0:
		if degrees < 67.0:
			if degrees < 22.0:
				return COMPASS_EAST
			return COMPASS_SOUTHEAST
		if degrees < 112.0:
			return COMPASS_SOUTH
		return COMPASS_SOUTHWEST
	if degrees < 247.0:
		if degrees < 202.0:
			return COMPASS_WEST
		return COMPASS_NORTHWEST
	if degrees < 337.0:
		if degrees < 292.0:
			return COMPASS_NORTH
		return COMPASS_NORTHEAST
	return COMPASS_EAST

def rad2compass(radians):
	"""
	Returns one of the "COMPASS_<direction>" constants.
	"""
	return deg2compass(math.degrees(radians))

def compass2deg(const):
	"""
	Returns the value in degrees of one of the "COMPASS_<direction>" constants.
	"""
	if const == COMPASS_NORTH: return 270.0
	if const == COMPASS_NORTHEAST: return 315.0
	if const == COMPASS_EAST: return 0.0
	if const == COMPASS_SOUTHEAST: return 45.0
	if const == COMPASS_SOUTH: return 90.0
	if const == COMPASS_SOUTHWEST: return 135.0
	if const == COMPASS_WEST: return 180.0
	if const == COMPASS_NORTHWEST: return 225.0
	raise KeyError("Invalid value for compass constant")

def compass2rad(const):
	"""
	Returns the value in radians of one of the "COMPASS_<direction>" constants.
	"""
	return math.radians(compass2deg(const))

def compass_str(const):
	"""
	Returns a string, such as "N", "NW", for the given compass direction constant.
	"""
	if const == COMPASS_NORTH: return "N"
	if const == COMPASS_NORTHEAST: return "NE"
	if const == COMPASS_EAST: return "E"
	if const == COMPASS_SOUTHEAST: return "SE"
	if const == COMPASS_SOUTH: return "S"
	if const == COMPASS_SOUTHWEST: return "SW"
	if const == COMPASS_WEST: return "W"
	if const == COMPASS_NORTHWEST: return "NW"
	raise KeyError("Invalid value for compass constant")

def triangular(value, reduction):
	"""
	Returns the number of times the "reduction" parameter must be applied to the
	"value" parameter for the value to reach zero.

	For example, "triangular(speed, deceleration)" will tell you how many frames it
	will take to decelerate from "speed" to zero, where "speed" and "deceleration"
	are measures of distance of travel in pixels per frame.
	"""
	return _inner_triangular(value + reduction, reduction)

def _inner_triangular(remainder, reduction):
	if remainder <= reduction: return reduction
	return remainder + _inner_triangular(remainder - reduction, reduction)

#  end legame/__init__.py
