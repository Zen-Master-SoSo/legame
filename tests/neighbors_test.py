import pytest, pygame
from legame3.sprite_enhancement import MovingSprite
from legame3.neighbors import Neighborhood, Neighbor, Quadrant


class AreaByCount(Neighborhood):
	cells_x = 4
	cells_y = 3


class AreaBySize(Neighborhood):
	cell_width = 100
	cell_height = 100


class Thing(MovingSprite, Neighbor):
	pass
	def __init__(self, area, x, y):
		MovingSprite.__init__(self, x, y)
		area.observe(self)
	def notice(self, neighbor):
		assert isinstance(neighbor, Neighbor)



def test_constructor():
	r = pygame.Rect(0, 0, 400, 300)

	# Calc height/width from cell count correctly
	a = AreaByCount(r)
	assert a.cell_width == 100
	assert a.cell_height == 100
	assert len(a.all_quadrants) == (a.cells_x - 1) * (a.cells_y - 1)
	assert len(a.cells) == a.cells_x
	assert len(a.cells[0]) == a.cells_y

	# Calc cell count from height/width correctly
	a = AreaBySize(r)
	assert a.cells_x == 4
	assert a.cells_y == 3
	assert len(a.all_quadrants) == (a.cells_x - 1) * (a.cells_y - 1)
	assert len(a.cells) == a.cells_x
	assert len(a.cells[0]) == a.cells_y


def test_quadrant_populated():
	# Check "quadrants" populated correctly:
	r = pygame.Rect(0, 0, 400, 300)
	a = AreaByCount(r)
	for quadrant in a.all_quadrants:
		assert isinstance(quadrant, Quadrant)


def test_cell_lookups_populated():
	# Check "cells" populated correctly:
	r = pygame.Rect(0, 0, 400, 300)
	a = AreaByCount(r)

	assert len(a.cells) == a.cells_x
	assert len(a.cells[0]) == a.cells_y

	# top-left cell (x=0, y=0):
	cell = a.cells[0][0]
	assert isinstance(cell, list)
	assert len(cell) == 1
	assert isinstance(cell[0], Quadrant)
	assert cell[0].x == 0
	assert cell[0].y == 0

	# top, second from the left (x=1, y=0):
	cell = a.cells[1][0]
	assert isinstance(cell, list)
	assert len(cell) == 2
	assert isinstance(cell[0], Quadrant)
	assert cell[0].x == 0
	assert cell[0].y == 0
	assert isinstance(cell[1], Quadrant)
	assert cell[1].x == 1
	assert cell[1].y == 0

	# top, third from the left (x=2, y=0):
	cell = a.cells[2][0]
	assert isinstance(cell, list)
	assert len(cell) == 2
	assert isinstance(cell[0], Quadrant)
	assert cell[0].x == 1
	assert cell[0].y == 0
	assert isinstance(cell[1], Quadrant)
	assert cell[1].x == 2
	assert cell[1].y == 0

	# top-right cell (x=3, y=0):
	cell = a.cells[3][0]
	assert isinstance(cell, list)
	assert len(cell) == 1
	assert isinstance(cell[0], Quadrant)
	assert cell[0].x == 2
	assert cell[0].y == 0

	# middle-left cell (x=0, y=1):
	cell = a.cells[0][1]
	assert isinstance(cell, list)
	assert len(cell) == 2
	assert isinstance(cell[0], Quadrant)
	assert cell[0].x == 0
	assert cell[0].y == 0
	assert isinstance(cell[1], Quadrant)
	assert cell[1].x == 0
	assert cell[1].y == 1

	# middle row, second from the left (x=1, y=1):
	cell = a.cells[1][1]
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

	# middle row, third from the left (x=2, y=1):
	cell = a.cells[2][1]
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

	# middle row, right (x=3, y=1):
	cell = a.cells[3][1]
	assert isinstance(cell, list)
	assert len(cell) == 2
	assert isinstance(cell[0], Quadrant)
	assert cell[0].x == 2
	assert cell[0].y == 0
	assert isinstance(cell[1], Quadrant)
	assert cell[1].x == 2
	assert cell[1].y == 1

	# bottom-left cell (x=0, y=2):
	cell = a.cells[0][2]
	assert isinstance(cell, list)
	assert len(cell) == 1
	assert isinstance(cell[0], Quadrant)
	assert cell[0].x == 0
	assert cell[0].y == 1

	# bottom row, second from the left (x=1, y=2):
	cell = a.cells[1][2]
	assert isinstance(cell, list)
	assert len(cell) == 2
	assert isinstance(cell[0], Quadrant)
	assert cell[0].x == 0
	assert cell[0].y == 1
	assert isinstance(cell[1], Quadrant)
	assert cell[1].x == 1
	assert cell[1].y == 1

	# bottom row, third from the left (x=2, y=2):
	cell = a.cells[2][2]
	assert isinstance(cell, list)
	assert len(cell) == 2
	assert isinstance(cell[0], Quadrant)
	assert cell[0].x == 1
	assert cell[0].y == 1
	assert isinstance(cell[1], Quadrant)
	assert cell[1].x == 2
	assert cell[1].y == 1

	# bottom-right (x=3, y=2):
	cell = a.cells[3][2]
	assert isinstance(cell, list)
	assert len(cell) == 1
	assert isinstance(cell[0], Quadrant)
	assert cell[0].x == 2
	assert cell[0].y == 1


def test_sprite_population():
	r = pygame.Rect(0, 0, 40, 30)
	a = AreaByCount(r)

	t1 = Thing(a, 5, 5)
	assert len(a._observed_sprites_list) == 1
	assert len(a.quadrant(0,0).sprites) == 0
	assert len(a.sprites_in(0,0)) == 0
	assert len(a.quadrant(0,0).sprites) == 0
	assert len(a.sprites_in(0,0)) == 0

	a.notify_sprites()
	assert len(a.quadrant(0,0).sprites) == 1
	assert len(a.sprites_in(0,0)) == 1

	t2 = Thing(a, 15, 15)
	a.notify_sprites()
	assert len(a.quadrant(0,0).sprites) == 2
	assert len(a.sprites_in(0,0)) == 2
	assert len(a.quadrant(1,1).sprites) == 1
	assert len(a.sprites_in(1,1)) == 1

	t3 = Thing(a, 25, 25)
	a.notify_sprites()
	assert len(a.quadrant(0,0).sprites) == 2
	assert len(a.sprites_in(0,0)) == 2
	assert len(a.quadrant(1,1).sprites) == 2
	assert len(a.sprites_in(1,1)) == 2
	assert len(a.quadrant(2,1).sprites) == 1
	assert len(a.sprites_in(2,1)) == 1

	t4 = Thing(a, 35, 15)
	a.notify_sprites()
	assert len(a.quadrant(0,0).sprites) == 2
	assert len(a.sprites_in(0,0)) == 2
	assert len(a.quadrant(1,1).sprites) == 2
	assert len(a.sprites_in(1,1)) == 2
	assert len(a.quadrant(2,1).sprites) == 2
	assert len(a.sprites_in(2,1)) == 2

