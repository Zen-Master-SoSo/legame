"""
Demonstrates board game moves, jumps, state changes, and animations
"""

import random
from pygame.locals import K_ESCAPE, K_q
from pygame import Rect
from pygame.sprite import Sprite
from legame.game import *
from legame.board_game import *
from legame.flipper import *
from legame.exit_states import *



class TestGame(BoardGame):

	def __init__(self, options=None):
		self.set_resource_dir_from_file(__file__)
		BoardGame.__init__(self, options)
		self.my_color = random.choice(["r", "g", "b"])

	def initial_state(self):
		return GSSelect(cell=None)



# Game states:

class GSBase(BoardGameState):
	"""
	Used as the base class of all game states defined in this module.
	ESCAPE or Q button quits game.
	"""

	def _evt_keydown(self, event):
		"""
		Exit game immediately if K_ESCAPE key pressed
		"""
		if event.key == K_ESCAPE or event.key == K_q:
			GSQuit()


class GSSelect(BoardGameState):
	"""
	Game state entered when the user must choose an empty space to fill, or their own block to move.
	attributes used:
		cell: the position that the last piece moved to, used as a reminder
	Example of changing state to this:
		GSSelect(cell=(x, y))
	"""

	may_click	= True	# May click on any block
	cell		= None

	def enter_state(self):
		Game.current.statusbar.write("GSSelect")
		self.reminder_timer = None if self.cell is None else Game.current.set_timeout(self.timeout, 4000)

	def click(self, cell, evt):
		if self.reminder_timer is not None:
			Game.current.clear_timeout(self.reminder_timer)
		if cell.is_mine():
			GSSelectMoveTarget(cell=cell)
		else:
			Block(cell, Game.current.my_color)
			self.cell = cell	# Used to jiggle the last piece moved
			self.reminder_timer = Game.current.set_timeout(self.timeout, 4000)

	def timeout(self):
		self.cell.piece().jiggle()

	def _evt_keydown(self, event):
		"""
		Exit game immediately if K_ESCAPE or "q" keys pressed
		"""
		if event.key == K_ESCAPE or event.key == K_q:
			GSQuit()


	def exit_state(self, next_state):
		if self.reminder_timer is not None:
			Game.current.clear_timeout(self.reminder_timer)


class GSSelectMoveTarget(BoardGameState):
	"""
	Game state entered after the user choses their own block, setting up for a move.
	attributes used:
		cell: the position of the block to move
	Example of changing state to this:
		GSSelectMoveTarget(cell=(x, y))
	"""

	may_click	= True	# May click on any block
	cell		= None

	def enter_state(self):
		self.selected_piece = self.cell.piece().glow()
		Game.current.statusbar.write("GSSelectMoveTarget")

	def click(self, cell, evt):
		self.selected_piece.unglow()
		if cell.is_mine():
			self.selected_piece = cell.piece().glow()
		else:
			Game.current.play("jump.wav")
			self.selected_piece.move_to(cell, lambda: GSSelect(cell=cell))

	def _evt_keydown(self, event):
		"""
		Exit game immediately if K_ESCAPE key pressed
		"""
		if event.key == K_ESCAPE or event.key == K_q:
			GSQuit()



# Sprites:

class Block(GamePiece, Flipper):

	def __init__(self, cell, color):
		self.image_folder = "Block/" + color
		GamePiece.__init__(self, cell, color)
		Flipper.__init__(self, FlipThrough("enter", fps=25), FlipNone())
		Game.current.play("enter.wav")
		self.__glow = None


	def update(self):
		GamePiece.update(self)
		Flipper.update(self)


	def jiggle(self):
		self.flip(FlipBetween("jiggle", loops=11, fps=30), FlipNone())
		return self


	def glow(self):
		self.__glow = Glow(self.cell)
		return self


	def unglow(self):
		if self.__glow:
			self.__glow.kill()
			self.__glow = None
		return self


	def kill(self):
		Game.current.play("bust.wav")
		Sprite.kill(self)



class Glow(Flipper, Sprite):

	def __init__(self, cell, frame=0):
		self.cell = cell
		self.rect = self.cell.rect()
		Sprite.__init__(self, Game.current.sprites)
		Game.current.sprites.change_layer(self, Game.LAYER_BELOW_PLAYER)
		Flipper.__init__(self, FlipBetween(loop_forever=True, frame=frame, fps=30))




if __name__ == '__main__':
	import argparse
	p = argparse.ArgumentParser()
	p.epilog = "Demonstrates board game moves, jumps, state changes, and animations"
	p.add_argument("--quiet", "-q", action="store_true", help="Don't make sound")
	p.add_argument("--verbose", "-v", action="store_true", help="Show more detailed debug information")
	p.exit(TestGame(p.parse_args()).run())



