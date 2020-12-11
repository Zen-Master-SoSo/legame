import pytest
from legame3.locals import *


def test_normal_degrees():
	for degrees in range(-3600, 3600, 45):
		assert normal_degrees(degrees) >= 0
		assert normal_degrees(degrees) <= 360

def test_normal_radians():
	radians = -TWO_PI * 3
	while radians <= TWO_PI * 3:
		assert normal_radians(radians) <= PI
		assert normal_radians(radians) >= -PI
		radians += TWO_PI / 8


def test_deg2side():
	assert deg2side(0) == SIDE_RIGHT
	assert deg2side(90) == SIDE_BOTTOM
	assert deg2side(180) == SIDE_LEFT
	assert deg2side(270) == SIDE_TOP
	assert deg2side(44) == SIDE_RIGHT
	assert deg2side(46) == SIDE_BOTTOM
	assert deg2side(134) == SIDE_BOTTOM
	assert deg2side(136) == SIDE_LEFT
	assert deg2side(224) == SIDE_LEFT
	assert deg2side(226) == SIDE_TOP
	assert deg2side(314) == SIDE_TOP
	assert deg2side(316) == SIDE_RIGHT

def test_rad2side():
	assert rad2side(math.radians(0)) == SIDE_RIGHT
	assert rad2side(math.radians(90)) == SIDE_BOTTOM
	assert rad2side(math.radians(180)) == SIDE_LEFT
	assert rad2side(math.radians(270)) == SIDE_TOP
	assert rad2side(math.radians(44)) == SIDE_RIGHT
	assert rad2side(math.radians(46)) == SIDE_BOTTOM
	assert rad2side(math.radians(134)) == SIDE_BOTTOM
	assert rad2side(math.radians(136)) == SIDE_LEFT
	assert rad2side(math.radians(224)) == SIDE_LEFT
	assert rad2side(math.radians(226)) == SIDE_TOP
	assert rad2side(math.radians(314)) == SIDE_TOP
	assert rad2side(math.radians(316)) == SIDE_RIGHT


