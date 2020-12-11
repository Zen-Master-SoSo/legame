"""Provides the BoardGame class, a framework for board games"""

import pygame
from pygame.locals import *
from pygame import Rect, Surface, mouse
from pygame.draw import line
from pygame.sprite import Sprite
from legame3.locals import *
from legame3.game import *
from legame3.sprite_enhancement import MovingSprite



class BoardGame(Game):

	board					= None
	statusbar				= None

	my_color				= None
	opponent_color			= None


	def initial_background(self, display_size):
		self.board = self.get_board()
		self.statusbar = self.get_statusbar()
		board_bg = self.board.initial_background(display_size)
		background = Surface((
			self.board.rect.width,
			self.board.rect.height + self.statusbar.rect.height
		))
		background.blit(board_bg, (0, 0))
		self.statusbar.rect.top = self.board.rect.height
		return background


	def get_board(self):
		return GameBoard()


	def get_statusbar(self):
		return Statusbar()



class GameBoard:

	columns				= 7
	rows				= 9
	cell_px				= 50

	background_color	= (0,0,0)
	grid_lines_color	= (80,80,80)

	background			= None

	def __init__(self, columns=None, rows=None):
		if columns: self.columns = columns
		if rows: self.rows = rows
		self.rect = Rect((0, 0, self.columns * self.cell_px, self.rows * self.cell_px + 1))
		self.__squares = [[None for y in range(self.rows)] for x in range(self.columns)]
		self.max_x = self.columns - 1
		self.max_y = self.rows - 1
		self.center_x = self.columns // 2
		self.center_y = self.rows // 2
		self.cell_half_px = self.cell_px // 2


	def initial_background(self, display_size):
		bg = Surface(self.rect.size)
		bg.fill(self.background_color)
		for col in range(self.columns):
			x = col * self.cell_px
			line(bg, self.grid_lines_color, (x, 0), (x, self.rect.height), 1)
		for row in range(self.rows + 1):
			y = row * self.cell_px
			line(bg, self.grid_lines_color, (0, y), (self.rect.width, y), 1)
		return bg


	# Set / get / inspect board positions:

	def piece_at(self, pos):
		return self.__squares[pos[0]][pos[1]]


	def clear_square(self, pos):
		self.__squares[pos[0]][pos[1]] = None
		return self


	def set_square(self, pos, piece):
		self.__squares[pos[0]][pos[1]] = piece
		return self


	def is_mine(self, pos):
		piece = self.piece_at(pos)
		return False if piece is None else piece.color == Game.current.my_color


	def is_my_opponents(self, pos):
		piece = self.piece_at(pos)
		return False if piece is None else piece.color == Game.current.opponent_color


	def is_empty(self, pos):
		return self.piece_at(pos) is None


	def rotate(self, pos):
		"""
		Returns a board position rotated 180 degrees.
		Used for showing opponent moves when the move is defined from their perspective.
		"""
		return (self.max_x - pos[0], self.max_y - pos[1])



class Statusbar(Sprite):

	padding				= 8
	font				= 'Ubuntu Light'
	font_size			= 22
	foreground_color	= (250,250,160)
	background_color	= (0,0,12)


	def __init__(self):
		Sprite.__init__(self, Game.current.sprites)
		Game.current.sprites.change_layer(self, Game.LAYER_PLAYER)
		self.font = pygame.font.SysFont(self.font, 22)
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

	mouse_pos		= None
	mouse_down_pos	= None


	def __init__(self, **kwargs):
		"""
		BoardGameState constructor - sets the current mouse position passes execution
		to GameState constructor.
		"""
		self.mouse_pos = mouse.get_pos()
		GameState.__init__(self, **kwargs)


	def loop_end(self):
		"""
		Cyclical function called at the end of Game.main_loop()
		Sets the mouse cursor based on the state of the "may_click" flag.
		"""
		if self.may_click:
			mouse.set_cursor(*pygame.cursors.arrow)
		else:
			mouse.set_cursor(*pygame.cursors.broken_x)


	def mousemotion(self, event):
		"""
		Mouse move event passed to this GameState.
		event will contain:	pos, rel, buttons
		"""
		y = event.pos[1] // Game.current.board.cell_px
		if y < Game.current.board.rows:
			x = event.pos[0] // Game.current.board.cell_px
			if x != self.mouse_pos[0] or y != self.mouse_pos[1]:
				self.mouse_exit(self.mouse_pos)
				self.mouse_pos = (x, y)
				self.mouse_enter(self.mouse_pos)
		else:
			self.may_click = True


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


	def mouse_enter(self, pos):
		"""
		"Pseudo" event which occurs after the mouse moved to a new position on the board.
		This event immediately follows "mouse_exit".
		"""
		pass


	def mouse_exit(self, pos):
		"""
		"Pseudo" event which occurs after the mouse moves out of a position on the board.
		This event is immediately followed by "mouse_enter" with the new position given.
		"""
		pass


	def click(self, pos, event):
		"""
		"Pseudo" event which occurs when the player presses and releases the mouse
		button over a single position.
		"pos" is the board position which was "clicked" (not screen_rect x/y).
		"event" is the pygame event passed to the "mousebuttonup" function, which
		will contain "pos" and "button" attributes.
		"""
		pass



class GamePiece(MovingSprite, Sprite):

	max_speed	= 17.0
	min_speed	= 0.5
	decel_rate	= 1.4


	def __init__(self, pos, color):
		self.pos = pos
		self.color = color
		x, y = self.mid_square(self.pos)
		MovingSprite.__init__(self, x, y)
		Sprite.__init__(self, Game.current.sprites)
		Game.current.sprites.change_layer(self, Game.LAYER_PLAYER)
		self.rect = Rect(0, 0, Game.current.board.cell_px, Game.current.board.cell_px)
		self.rect.centerx = int(self.position.x)
		self.rect.centery = int(self.position.y)
		self.image_set = Game.current.resources.image_set("%s/%s" % (self.__class__.__name__, self.color))
		Game.current.board.set_square(pos, self)


	def mid_square(self, pos_tuple):
		return (
			pos_tuple[0] * Game.current.board.cell_px + Game.current.board.cell_half_px,
			pos_tuple[1] * Game.current.board.cell_px + Game.current.board.cell_half_px
		)


	# Move routines which may be called in the "update()" function of the parent Sprite:

	def travel_to_pos(self, target_pos, on_arrival=None):
		"""
		High-level command which sets this GamePiece on a path towards a given square.
		Each subsequent call to "move()" will move it one frame closer to the target_pos.
		When travel is complete, the optional "on_arrival" function will be called.
		This function overrides the base function in MovingSprite in order to convert board square
		positions to pixel coordinates and update the game board when travel is complete.
		"""
		def arrival_function():
			self.pos = self.target_pos
			current_resident = Game.current.board.piece_at(self.pos)
			if current_resident is not None:
				current_resident.kill()
			Game.current.board.set_square(self.pos, self)
			self._motion_function = self.no_motion
			if on_arrival is not None:
				on_arrival()
		Game.current.board.clear_square(self.pos)
		self.target_pos = target_pos
		return self.travel_to(self.mid_square(target_pos), arrival_function)



