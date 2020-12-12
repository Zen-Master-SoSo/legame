"""Provides the BoardGame class, a framework for board games"""

from math import floor
from pygame.font import SysFont
from pygame.locals import *
from pygame.cursors import arrow, broken_x
from pygame import Rect, Surface, mouse
from pygame.draw import line
from pygame.sprite import Sprite
from legame.locals import *
from legame.game import *
from legame.sprite_enhancement import MovingSprite



class BoardGame(Game):

	board					= None
	statusbar				= None

	my_color				= None
	opponent_color			= None


	def __init__(self, options=None):
		"""
		BoardGame constructor; calls Game.__init__() and instantiates the GameBoard and
		"""
		Game.__init__(self, options)
		self.board = self.get_board()
		self.statusbar = Statusbar()


	def initial_background(self, display_size):
		self.statusbar.rect.top = self.board.rect.height
		board_bg = self.board.initial_background(display_size)
		my_background = Surface((
			self.board.rect.width,
			self.board.rect.height + self.statusbar.rect.height
		))
		my_background.blit(board_bg, (0, 0))
		return my_background


	def get_board(self):
		return GameBoard()




class GameBoard:

	columns				= 7
	rows				= 9
	cell_width			= 50
	cell_height			= 50
	left				= 0
	top					= 0

	background_color	= (0,0,0)
	grid_lines_color	= (80,80,80)

	background			= None


	def __init__(self, columns=None, rows=None):
		if columns: self.columns = columns
		if rows: self.rows = rows
		self.rect = Rect((self.left, self.top, self.columns * self.cell_width, self.rows * self.cell_height + 1))
		self.__cells = [[None for y in range(self.rows)] for x in range(self.columns)]
		self.max_column = self.columns - 1
		self.max_row = self.rows - 1
		self.center_column = self.columns // 2
		self.center_row = self.rows // 2
		self.cell_half_width = self.cell_width // 2
		self.cell_half_height = self.cell_height // 2


	def initial_background(self, display_size):
		bg = Surface(self.rect.size)
		bg.fill(self.background_color)
		for col in range(self.columns):
			x = col * self.cell_width
			line(bg, self.grid_lines_color, (x, 0), (x, self.rect.height), 1)
		for row in range(self.rows + 1):
			y = row * self.cell_height
			line(bg, self.grid_lines_color, (0, y), (self.rect.width, y), 1)
		return bg


	# Set / get / inspect board positions:

	def cell_at(self, *args):
		"""
		Return a BoardPosition from screen coordinates.
		Args may be a pair of numbers (float or int), or a tuple of numbers (float or int).
		Returns None if the coordinates are outside of the board.
		"""
		def throw_up():
			raise ValueError("Board.cell_at() takes two numbers or a tuple of two numbers as arguments")
		if len(args) == 1:
			if not isinstance(args[0], tuple): throw_up()
			if len(args[0]) != 2: throw_up()
			if not isinstance(args[0][0], int) and not isinstance(args[0][0], float): throw_up()
			if not isinstance(args[0][1], int) and not isinstance(args[0][1], float): throw_up()
			x, y = args[0]
		elif len(args) == 2:
			if not isinstance(args[0], int) and not isinstance(args[0], float): throw_up()
			if not isinstance(args[1], int) and not isinstance(args[1], float): throw_up()
			x, y = args
		else:
			throw_up()
		return BoardPosition(
			floor((x - Game.current.board.left) / Game.current.board.cell_width),
			floor((y - Game.current.board.top) / Game.current.board.cell_height)
		) if Game.current.board.rect.collidepoint(x, y) else None


	def piece_at(self, cell):
		"""
		Returns a reference to the GamePiece occupying the given cell.
		If no piece occupies the cell, returns None.
		"""
		assert isinstance(cell, BoardPosition)
		return self.__cells[cell.column][cell.row]


	def clear_square(self, cell):
		"""
		Kills the GamePiece at the given cell, if one exists there.
		"""
		assert isinstance(cell, BoardPosition)
		self.__cells[cell.column][cell.row] = None
		return self


	def set_square(self, cell, piece):
		"""
		Places a reference to the given GamePiece in the given square.
		"""
		assert isinstance(cell, BoardPosition)
		assert isinstance(piece, GamePiece)
		self.__cells[cell.column][cell.row] = piece
		return self


	def is_mine(self, cell):
		"""
		Returns True if there is a GamePiece at the given cell, and it is this player's "color".
		"""
		assert isinstance(cell, BoardPosition)
		piece = self.piece_at(cell)
		return False if piece is None else piece.color == Game.current.my_color


	def opponent_at(self, cell):
		"""
		Returns True if there is a GamePiece at the given cell, and it is not this player's "color".
		"""
		assert isinstance(cell, BoardPosition)
		piece = self.piece_at(cell)
		return False if piece is None else piece.color != Game.current.my_color


	def is_empty(self, cell):
		"""
		Returns True if the given cell is empty.
		"""
		assert isinstance(cell, BoardPosition)
		return self.piece_at(cell) is None


	def rotate(self, cell):
		"""
		Returns a board position rotated 180 degrees.
		Used for showing opponent moves when the move is defined from their perspective.
		"""
		assert isinstance(cell, BoardPosition)
		return (self.max_column - cell.column, self.max_row - cell.row)



class BoardPosition:


	def __init__(self, column, row):
		self.column, self.row = column, row


	def screen_coordinates(self):
		"""
		Returns the center point of this position.
		"""
		return (
			Game.current.board.left + Game.current.board.cell_width * self.column + Game.current.board.cell_half_width,
			Game.current.board.top + Game.current.board.cell_height * self.row + Game.current.board.cell_half_height
		)


	def get_rect(self):
		"""
		Returns a pygame rect which covers this position.
		Top-left is the top-left of the cell.
		"""
		return Rect(
			Game.current.board.left + Game.current.board.cell_width * self.column,
			Game.current.board.top + Game.current.board.cell_height * self.row,
			Game.current.board.cell_width,
			Game.current.board.cell_height
		)


	def __str__(self):
		return "BoardPosition: column {}, row {}".format(self.column, self.row)



class Statusbar(Sprite):

	padding				= 8
	font				= 'Ubuntu Light'
	font_size			= 22
	foreground_color	= (250,250,160)
	background_color	= (0,0,12)


	def __init__(self):
		Sprite.__init__(self, Game.current.sprites)
		Game.current.sprites.change_layer(self, Game.LAYER_PLAYER)
		self.font = SysFont(self.font, 22)
		self.image = Surface((
			Game.current.board.rect.width,
			self.font.get_linesize() + self.padding * 2
		))
		self.text = ""
		self.rect = self.image.get_rect()


	def clear(self):
		self.image.fill(self.background_color)


	def write(self, text, color=None):
		self.text = text
		if color is not None: self.foreground_color = color
		self._update()


	def append(self, text):
		self.text = self.text + text
		self._update()


	def _update(self):
		self.clear()
		self.image.blit(
			self.font.render(self.text, True, self.foreground_color),
			(self.padding, self.padding)
		)



class BoardGameState(GameState):

	mouse_down_pos	= None
	may_click		= False


	def __init__(self, **kwargs):
		"""
		BoardGameState constructor - sets the current mouse position passes execution
		to GameState constructor.
		"""
		self.mouse_pos = Game.current.board.cell_at(mouse.get_pos())
		GameState.__init__(self, **kwargs)


	def loop_end(self):
		"""
		Cyclical function called at the end of Game._main_loop()
		Sets the mouse cursor based on the state of the "may_click" flag.
		"""
		if self.may_click:
			mouse.set_cursor(*arrow)
		else:
			mouse.set_cursor(*broken_x)


	def mousemotion(self, event):
		"""
		Mouse move event passed to this GameState.
		event will contain:	pos, rel, buttons
		"""
		cell = Game.current.board.cell_at(event.pos)
		if cell is None: return
		if self.mouse_pos is not None and (cell.column != self.mouse_pos.column or cell.row != self.mouse_pos.row):
			self.mouse_exit(self.mouse_pos)
			self.mouse_enter(cell)
		self.mouse_pos = cell


	def mousebuttondown(self, event):
		"""
		Mouse down event passed to this GameState.
		event will contain:	pos, button
		"""
		self.mouse_down_pos = self.mouse_pos


	def mousebuttonup(self, event):
		"""
		Mouse up event passed to this GameState.
		event will contain: pos, button
		"""
		if self.may_click and self.mouse_down_pos == self.mouse_pos:
			self.click(self.mouse_pos, event)


	def mouse_enter(self, cell):
		"""
		"Pseudo" event which occurs after the mouse moved to a new position on the board.
		This event immediately follows "mouse_exit".
		"""
		pass


	def mouse_exit(self, cell):
		"""
		"Pseudo" event which occurs after the mouse moves out of a position on the board.
		This event is immediately followed by "mouse_enter" with the new position given.
		"""
		pass


	def click(self, cell, event):
		"""
		"Pseudo" event which occurs when the player presses and releases the mouse
		button over a single position.
		"cell" is the board position which was "clicked" (not screen_rect x/y).
		"event" is the pygame event passed to the "mousebuttonup" function, which
		will contain "pos" and "button" attributes.
		"""
		pass



class GamePiece(MovingSprite, Sprite):

	max_speed	= 17.0
	min_speed	= 0.5
	decel_rate	= 1.4


	def __init__(self, cell, color):
		self.cell = cell
		self.color = color
		Sprite.__init__(self, Game.current.sprites)
		Game.current.sprites.change_layer(self, Game.LAYER_PLAYER)
		x, y = self.cell.screen_coordinates()
		MovingSprite.__init__(self, x, y)
		self.rect = self.cell.get_rect()
		self.image_set = Game.current.resources.image_set("%s/%s" % (self.__class__.__name__, self.color))
		Game.current.board.set_square(cell, self)



	# Move routines which may be called in the "update()" function of the parent Sprite:

	def travel_to_cell(self, target_cell, on_arrival=None):
		"""
		High-level command which sets this GamePiece on a path towards a given square.
		Each subsequent call to "move()" will move it one frame closer to "target_cell".
		When travel is complete, the optional "on_arrival" function will be called.
		This function overrides the base function in MovingSprite in order to convert board square
		positions to pixel coordinates and update the game board when travel is complete.
		"""
		def arrival_function():
			self.cell = self.target_cell
			current_resident = Game.current.board.piece_at(self.cell)
			if current_resident is not None:
				current_resident.kill()
			Game.current.board.set_square(self.cell, self)
			self._motion_function = self.no_motion
			if on_arrival is not None:
				on_arrival()
		Game.current.board.clear_square(self.cell)
		self.target_cell = target_cell
		print(self.target_cell)
		return self.travel_to(target_cell.screen_coordinates(), arrival_function)



