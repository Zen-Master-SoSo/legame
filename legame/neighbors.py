"""
Provides a means for dividing up the screen into sub-sections within which MovingSprites are
cross-checked for nearness to each other. This allows MovingSprite instances to modify their
behavior on the basis of their proximity to other MovingSprites, without having to cross-check
every instance on the screen against every other instance.
"""

from math import floor, ceil


class Neighborhood:
	"""
	Divides an area of the screen into "Quadrant"s which are used to determine
	which sprites (or any thing really) are nearby which others.

	Quadrants are a series of squares which overlap on both the x, y axes. This
	reduces the search space when determining whether two things need to be
	notified of each other's existence.

	This can best be described visually. This is a representation of an
	Neighborhood covering a 4x3 grid. It spans 3 Quadrants on the x axis, (labeled
	0, 1, 2) and 2 quadrants on the y axis (labeled 0, 1). Inside of each cell in
	the illustration is a list of the x,y coordinates of all of the the quadrants
	which overlap that cell:

		---------------------
		|         0         |
		          ---------------------
		          |         1         |
		                    ---------------------
		                    |         2         |
		-----------------------------------------  ---
		| 0,0     | 0,0     |     2,0 |     2,0 |     |
		|         |   1,0   |   1,0   |         |     |
		|         |         |         |         |     |
		|         |         |         |         |     |
		-----------------------------------------  0  | ---
		| 0,0     | 0,0     |     2,0 |     2,0 |     |    |
		|         |   1,0   |   1,0   |         |     |    |
		|         |   1,1   |   1,1   |         |     |    |
		| 0,1     | 0,1     |     2,1 |     2,1 |     |    |
		-----------------------------------------  ---   1 |
		|         |         |         |         |          |
		|         |         |         |         |          |
		|         |   1,1   |   1,1   |         |          |
		| 0,1     | 0,1     |     2,1 |     2,1 |          |
		-----------------------------------------  --------

	Notice that each quadrant takes up four cells, and each cell shares at least
	one quadrant with all the cells surrounding it (above-left, above, above-right,
	left, right, below-left, below, below-right - 8 in total).

	Let's take a close look at the third cell from the left, third from the top.
	It is covered by two quadrants:
		1,1  2,1

	The cell immediately above it is in these quadrants:
		2,0  1,0  1,1  2,1
	... so these two cells are both in quadrant 1,1, and both in quadrant 2,1

	The cell above and to the left (second from left, second from top), is
	contained in these quadrants:
		0,0  1,0  1,1  0,1
	... so our cell (three cells from the left, three cells from the top), shares
	only quadrant 1,1

	The cell above and to the right (fourth from left, second from top), is
	contained in these quadrants:
		2,0  2,1
	... so our cell (three cells from the left, three cells from the top), shares
	only quadrant 2,1

	When an "observed" sprite is placed, it is given membership in the quadrants
	which contain the cell that it is in. Detecting interaction between sprites is
	done for every quadrant, and that reduces the amount of comparisons neccessary
	between sprites.

	To use a Neighborhood, instantiate the Neighborhood class, add the sprites you
	want notified of each other's existence using the "observe" function when they
	are instantiated, and call the "notify_sprites" function of the Neighborhood
	periodically. Typically this involves overriding the "_end_loop" function of
	the Game class and calling "notify_sprites" from there. Alternatively, you
	could call "notify_sprites" in a GameState's "loop_end" function. The only
	drawback to the second method is that you need to make sure that this call is
	made from every GameState which needs it.

	Don't forget to call the "ignore" function if/when a sprite is killed.
	Otherwise, it will remain in the list of observed sprites, and all the math
	necessary for keeping track of it will still be done. That will slow down
	your game. You might put a call to the "Neighborhood.ignore" function in the
	sprite's "kill" function.
	"""

	def __init__(self, rect, cells_x, cells_y):
		"""
		Set the area to be watched by this Neighborhood.
		(God, that sounds so Orwellian!)

		When constructing a Neighborhood, you must pass the following required
		arguments:

		rect (pygame.Rect): Identifies the area encompassing the Neighborhood.
							Only sprites in this rect will be notified of each
							others' existence. Normally,  this will be the
							Game.screen_rect, or some similar play area.
		cells_x (int)	  : The number of "cells" to divide the Neighborhood into
							on the x-axis - not "quadrants". A "quadrant" spans 3
							cells across. See the docstring for this module for a
							full explanation.
		cells_y (int)	  : The number of "cells" to divide the Neighborhood into
							on the y-axis - not "quadrants". (See "cells_x" above.)
		"""

		# Initialize either height/width based on cells_x/cells_y, or cells_x/cells_y based on height/width:
		self.rect = rect
		self.cells_x = cells_x
		self.cells_y = cells_y
		self.cell_width = self.rect.width / cells_x
		self.cell_height = self.rect.height / cells_y

		# self._quadrants is a flat, 1-dimensional list of Quadrant objects.
		# Each quadrant has an .x and .y attribute, corresponding to the first "cell" it covers.
		self._quadrants = []

		# self.__quadrant_maps is a two-dimensional which contains all the Quadrant instances, ordered by
		# their x,y coordinate which is the coordinate of the top-left cell covered by the Quadrant
		# First indice is the "x" axis, second indice is the "y" axis
		self.__quadrant_maps = [ [ None for y in range(0, self.cells_y - 1) ] for x in range(self.cells_x - 1) ]
		for x in range(self.cells_x - 1):
			for y in range(0, self.cells_y - 1):
				self._quadrants.append(Quadrant(x, y))
				self.__quadrant_maps[x][y] = self._quadrants[len(self._quadrants) - 1]

		self.count = len(self._quadrants)

		# self.cell_lookup is a 2-dimensional list, each element of which will contain a list of
		# references to the Quadrant instances which overlap that cell:
		self.__cell2quad_maps = [ [ [] for y in range(self.cells_y) ] for x in range(self.cells_x) ]

		# In a 4x3 grid, these are the class attributes:
		# cells_x:		4	- which makes for 3 quadrants across
		# cells_y:		3	- which makes for 2 quadrants down
		# quadrants:	3-across, with "x" indexes of 0, 1, 2;      2-down, with "y" indexes of 0, 1
		# __cell2quad_maps:	4-across, with "x" indexes of 0, 1, 3, 3;   3-down, with "y" indexes of 0, 1, 2
		#
		# Populate lookup tables:
		for x in range(self.cells_x - 1):			# in a 4x3 grid, iterate through 0, 1, 2
			for y in range(self.cells_y - 1):		# in a 4x3 grid, iterate through 0, 1
				for span_x in range(2):				# iterate through 0, 1
					#if x + span_x == self.cells_x: continue
					for span_y in range(2):			# iterate through 0, 1
						#if y + span_y == self.cells_y: continue
						self.__cell2quad_maps[x + span_x][y + span_y].append(self.__quadrant_maps[x][y])

		# self._observed_sprites_list are a list of all sprites to keep track of in the area:
		self._observed_sprites_list = []


	@property
	def cells(self):
		"""
		Returns a cell-to-quadrants list - really only should be used for testing.
		"""
		return self.__cell2quad_maps


	@property
	def all_quadrants(self):
		"""
		Returns the list of Quadrant objects - really only should be used for testing.
		"""
		return self._quadrants


	def sprites_in(self, x, y):
		"""
		Returns a list of sprites which occupy the quadrant specified by the given x/y coordinates.
		"""
		return self.__quadrant_maps[x][y].sprites


	def quadrant(self, x, y):
		"""
		Returns the single quadrant whose "top-left cell" occupies the "cell" x/y position given.
		"""
		return self.__quadrant_maps[x][y]


	def observe(self, sprite):
		"""
		Add a sprite to observe.
		You can add the same sprite more than once. All it will do is slow down your game.
		Don't do that.
		"""
		self._observed_sprites_list.append(sprite)


	def ignore(self, sprite):
		"""
		Remove a sprite from the list of sprites to observe.
		Hopefully, you haven't added it twice, because if so, it'll still be here.
		"""
		self._observed_sprites_list.remove(sprite)


	def notify_sprites(self):
		"""
		Re-calculate quadrant membership of all the sprites observed and notify the observed sprites
		when another observed sprite is within the same quadrant.
		"""
		for quadrant in self._quadrants:
			quadrant.sprites.clear()
		for sprite in self._observed_sprites_list:
			try:
				for quadrant in self.__cell2quad_maps[floor(sprite.x / self.cell_width)][floor(sprite.y / self.cell_height)]:
					quadrant.sprites.append(sprite)
			except IndexError:
				pass
		for quadrant in self._quadrants:
			cnt = len(quadrant.sprites)
			if cnt > 1:
				for a in range(cnt - 1):
					for b in range(a + 1, cnt):
						quadrant.sprites[a].notice(quadrant.sprites[b])
						quadrant.sprites[b].notice(quadrant.sprites[a])



class Quadrant:
	"""
	Division of an Neighborhood which covers at most 9 "cells".
	"""

	def __init__(self, x, y):
		self.x = x			# These values (and this whole class, really) are only
		self.y = y			# Used for debugging. The meat of this class is "sprites".
		self.sprites = []	# A list of sprites which are determined to be in this Quadrant.



class Neighbor:
	"""
	Demonstrates an implementation of the "notice" function, which is called when two things are within
	the same quadrant.
	"""

	def notice(self, neighbor):
		"""
		Informs this sprite that there's another sprite within a quadrant distance, allowing it
		"decide" what to do with the neighboring sprite.
		"""
		pass




