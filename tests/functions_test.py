#  legame/tests/functions_test.py
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
from math import radians
from legame import deg2side, rad2side, normal_radians, normal_degrees, \
	SIDE_LEFT, SIDE_TOP, SIDE_RIGHT, SIDE_BOTTOM, PI, TWO_PI

def test_normal_degrees():
	for degrees in range(-3600, 3600, 45):
		assert normal_degrees(degrees) >= 0
		assert normal_degrees(degrees) <= 360

def test_normal_radians():
	rad = -TWO_PI * 3
	while rad <= TWO_PI * 3:
		assert normal_radians(rad) <= PI
		assert normal_radians(rad) >= -PI
		rad += TWO_PI / 8

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
	assert rad2side(radians(0)) == SIDE_RIGHT
	assert rad2side(radians(90)) == SIDE_BOTTOM
	assert rad2side(radians(180)) == SIDE_LEFT
	assert rad2side(radians(270)) == SIDE_TOP
	assert rad2side(radians(44)) == SIDE_RIGHT
	assert rad2side(radians(46)) == SIDE_BOTTOM
	assert rad2side(radians(134)) == SIDE_BOTTOM
	assert rad2side(radians(136)) == SIDE_LEFT
	assert rad2side(radians(224)) == SIDE_LEFT
	assert rad2side(radians(226)) == SIDE_TOP
	assert rad2side(radians(314)) == SIDE_TOP
	assert rad2side(radians(316)) == SIDE_RIGHT


#  end legame/tests/functions_test.py
