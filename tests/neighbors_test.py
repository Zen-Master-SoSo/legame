#  legame/tests/neighbors_test.py
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
from pygame import Rect
from legame.sprite_enhancement import MovingSprite
from legame.neighbors import Neighborhood, Neighbor, Quadrant


class Thing(MovingSprite, Neighbor):
	pass
	def __init__(self, area, x, y):
		MovingSprite.__init__(self, x, y)
		area.observe(self)
	def notice(self, neighbor):
		assert isinstance(neighbor, Neighbor)


def test_constructor():
	rect = Rect(0, 0, 400, 300)

	# Calc height/width from cell count correctly
	nh = Neighborhood(rect, 4, 3)
	assert nh.cell_width == 100
	assert nh.cell_height == 100
	assert len(nh.all_quadrants) == (nh.cells_x - 1) * (nh.cells_y - 1)
	assert len(nh.cells) == nh.cells_x
	assert len(nh.cells[0]) == nh.cells_y

	# Check "quadrants" populated correctly:
	for quadrant in nh.all_quadrants:
		assert isinstance(quadrant, Quadrant)

	# Check "cells" populated correctly:
	assert len(nh.cells) == nh.cells_x
	assert len(nh.cells[0]) == nh.cells_y

	# top-left cell (x = 0, y = 0):
	cell = nh.cells[0][0]
	assert isinstance(cell, list)
	assert len(cell) == 1
	assert isinstance(cell[0], Quadrant)
	assert cell[0].x == 0
	assert cell[0].y == 0

	# top, second from the left (x = 1, y = 0):
	cell = nh.cells[1][0]
	assert isinstance(cell, list)
	assert len(cell) == 2
	assert isinstance(cell[0], Quadrant)
	assert cell[0].x == 0
	assert cell[0].y == 0
	assert isinstance(cell[1], Quadrant)
	assert cell[1].x == 1
	assert cell[1].y == 0

	# top, third from the left (x = 2, y = 0):
	cell = nh.cells[2][0]
	assert isinstance(cell, list)
	assert len(cell) == 2
	assert isinstance(cell[0], Quadrant)
	assert cell[0].x == 1
	assert cell[0].y == 0
	assert isinstance(cell[1], Quadrant)
	assert cell[1].x == 2
	assert cell[1].y == 0

	# top-right cell (x = 3, y = 0):
	cell = nh.cells[3][0]
	assert isinstance(cell, list)
	assert len(cell) == 1
	assert isinstance(cell[0], Quadrant)
	assert cell[0].x == 2
	assert cell[0].y == 0

	# middle-left cell (x = 0, y = 1):
	cell = nh.cells[0][1]
	assert isinstance(cell, list)
	assert len(cell) == 2
	assert isinstance(cell[0], Quadrant)
	assert cell[0].x == 0
	assert cell[0].y == 0
	assert isinstance(cell[1], Quadrant)
	assert cell[1].x == 0
	assert cell[1].y == 1

	# middle row, second from the left (x = 1, y = 1):
	cell = nh.cells[1][1]
	assert isinstance(cell, list)
	assert len(cell) == 4
	assert isinstance(cell[0], Quadrant)
	assert cell[0].x == 0
	assert cell[0].y == 0
	assert isinstance(cell[1], Quadrant)
	assert cell[1].x == 0
	assert cell[1].y == 1
	assert isinstance(cell[2], Quadrant)
	assert cell[2].x == 1
	assert cell[2].y == 0
	assert isinstance(cell[3], Quadrant)
	assert cell[3].x == 1
	assert cell[3].y == 1

	# middle row, third from the left (x = 2, y = 1):
	cell = nh.cells[2][1]
	assert isinstance(cell, list)
	assert len(cell) == 4
	assert isinstance(cell[0], Quadrant)
	assert cell[0].x == 1
	assert cell[0].y == 0
	assert isinstance(cell[1], Quadrant)
	assert cell[1].x == 1
	assert cell[1].y == 1
	assert isinstance(cell[2], Quadrant)
	assert cell[2].x == 2
	assert cell[2].y == 0
	assert isinstance(cell[3], Quadrant)
	assert cell[3].x == 2
	assert cell[3].y == 1

	# middle row, right (x = 3, y = 1):
	cell = nh.cells[3][1]
	assert isinstance(cell, list)
	assert len(cell) == 2
	assert isinstance(cell[0], Quadrant)
	assert cell[0].x == 2
	assert cell[0].y == 0
	assert isinstance(cell[1], Quadrant)
	assert cell[1].x == 2
	assert cell[1].y == 1

	# bottom-left cell (x = 0, y = 2):
	cell = nh.cells[0][2]
	assert isinstance(cell, list)
	assert len(cell) == 1
	assert isinstance(cell[0], Quadrant)
	assert cell[0].x == 0
	assert cell[0].y == 1

	# bottom row, second from the left (x = 1, y = 2):
	cell = nh.cells[1][2]
	assert isinstance(cell, list)
	assert len(cell) == 2
	assert isinstance(cell[0], Quadrant)
	assert cell[0].x == 0
	assert cell[0].y == 1
	assert isinstance(cell[1], Quadrant)
	assert cell[1].x == 1
	assert cell[1].y == 1

	# bottom row, third from the left (x = 2, y = 2):
	cell = nh.cells[2][2]
	assert isinstance(cell, list)
	assert len(cell) == 2
	assert isinstance(cell[0], Quadrant)
	assert cell[0].x == 1
	assert cell[0].y == 1
	assert isinstance(cell[1], Quadrant)
	assert cell[1].x == 2
	assert cell[1].y == 1

	# bottom-right (x = 3, y = 2):
	cell = nh.cells[3][2]
	assert isinstance(cell, list)
	assert len(cell) == 1
	assert isinstance(cell[0], Quadrant)
	assert cell[0].x == 2
	assert cell[0].y == 1

def test_sprite_population():
	rect = Rect(0, 0, 40, 30)
	nh = Neighborhood(rect, 4, 3)

	t1 = Thing(nh, 5, 5)
	assert len(nh._observed_sprites_list) == 1
	assert len(nh.quadrant(0,0).sprites) == 0
	assert len(nh.sprites_in(0,0)) == 0
	assert len(nh.quadrant(0,0).sprites) == 0
	assert len(nh.sprites_in(0,0)) == 0

	nh.notify_sprites()
	assert len(nh.quadrant(0,0).sprites) == 1
	assert len(nh.sprites_in(0,0)) == 1

	t2 = Thing(nh, 15, 15)
	nh.notify_sprites()
	assert len(nh.quadrant(0,0).sprites) == 2
	assert len(nh.sprites_in(0,0)) == 2
	assert len(nh.quadrant(1,1).sprites) == 1
	assert len(nh.sprites_in(1,1)) == 1

	t3 = Thing(nh, 25, 25)
	nh.notify_sprites()
	assert len(nh.quadrant(0,0).sprites) == 2
	assert len(nh.sprites_in(0,0)) == 2
	assert len(nh.quadrant(1,1).sprites) == 2
	assert len(nh.sprites_in(1,1)) == 2
	assert len(nh.quadrant(2,1).sprites) == 1
	assert len(nh.sprites_in(2,1)) == 1

	t4 = Thing(nh, 35, 15)
	nh.notify_sprites()
	assert len(nh.quadrant(0,0).sprites) == 2
	assert len(nh.sprites_in(0,0)) == 2
	assert len(nh.quadrant(1,1).sprites) == 2
	assert len(nh.sprites_in(1,1)) == 2
	assert len(nh.quadrant(2,1).sprites) == 2
	assert len(nh.sprites_in(2,1)) == 2


#  end legame/tests/neighbors_test.py
