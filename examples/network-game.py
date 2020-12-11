"""
Demonstrates sending moves over a network.
"""

import random
from legame.game import *
from legame.board_game import *
from legame.flipper import *
from legame.network_game import NetworkGame
from legame.examples.exit_states import GSQuit
from cable_car.json_messages import Message, MsgIdentify, MsgJoin, MsgRetry, MsgQuit


class TestGame(BoardGame, NetworkGame):

	def __init__(self, options=None):
		self.set_resource_dir_from_file(__file__)
		assert os.path.isdir(self.resource_dir)
		Game.__init__(self, options=None)
		NetworkGame.__init__(self)


	def get_board(self):
		return GameBoard(4, 4)


	def initial_state(self):
		global board, statusbar, send, me, my_opponent
		board = Game.current.board
		statusbar = Game.current.statusbar
		send = Game.current.messenger.send
		return GSWhoGoesFirst()



# Messages:

class MsgAdd(Message):

	def __init__(self, pos=None):
		self.pos = pos


	def rotate(self):
		self.pos = Game.current.board.rotate(self.pos)
		return self



class MsgPickAColor(Message):
	def __init__(self, color=None, number=None):
		self.color = random.choice(["r", "g", "b"])
		self.number = random.randint(0,999)



# Game states:

class GSBase(GameState):
	"""
	Used as the base class of all game states defined in this module.
	ESCAPE or Q button quits game.
	"""

	def keydown(self, event):
		"""
		Exit game immediately if K_ESCAPE key pressed
		"""
		if event.key == K_ESCAPE or event.key == K_q:
			GSQuit()



class GSWhoGoesFirst(GSBase):

	may_click	= False


	def enter_state(self):
		self.pick_a_color()


	def pick_a_color(self):
		self.picked = MsgPickAColor()
		send(self.picked)
		statusbar.write("Sent MsgPickAColor (%s:%d)" % (self.picked.color, self.picked.number))


	def handle_message(self, message):
		if isinstance(message, MsgPickAColor):
			if message.number == self.picked.number or message.color == self.picked.color:
				self.pick_a_color()
			else:
				Game.current.my_color = self.picked.color
				Game.current.opponent_color = message.color
				if message.number > self.picked.number:
					GSMyMove()
				else:
					GSWaitYourTurn()
		elif isinstance(message, MsgQuit):
			GSQuit()
		else:
			raise Exception("Unexpected message: %s" % message)



class GSMyMove(GSBase):


	def enter_state(self):
		statusbar.write("GSMyMove")
		Game.current.set_timeout(self.timeout, 250)


	def timeout(self, args):
		for x in range(board.columns):
			for y in range(board.rows):
				if board.piece_at((x, y)) is None:
					Block((x, y), Game.current.my_color)
					send(MsgAdd((x, y)))
					GSWaitYourTurn()
					return
		send(MsgQuit())
		GSQuit()



class GSWaitYourTurn(GSBase):


	def enter_state(self):
		statusbar.write("GSWaitYourTurn")


	def handle_message(self, message):
		if isinstance(message, MsgAdd):
			message.rotate()
			board.set_square(message.pos, Block(message.pos, Game.current.opponent_color))
		elif isinstance(message, MsgQuit):
			GSQuit()
		else:
			raise Exception("Unexpected message: %s" % message)
		GSMyMove()




# Game pieces and other sprites:

class Block(GamePiece, Flipper):

	def __init__(self, pos, color):
		self.image_base = "Block/" + color
		GamePiece.__init__(self, pos, color)
		Flipper.__init__(self, CycleThrough("enter", fps=25), CycleNone())
		self.__glow = None

	def update(self):
		GamePiece.update(self)
		Flipper.update(self)

	def jiggle(self):
		self.image_cycle(CycleBetween("jiggle", loops=11, fps=30), CycleNone())
		return self

	def glow(self):
		self.__glow = Glow(self.pos)
		return self

	def unglow(self):
		if self.__glow:
			self.__glow.kill()
			self.__glow = None
		return self



class Glow(Flipper, pygame.sprite.Sprite):

	def __init__(self, pos, frame=0):
		self.pos = pos
		pygame.sprite.Sprite.__init__(self, Game.current.sprites)
		Game.current.sprites.change_layer(self, Game.LAYER_BELOW_PLAYER)
		Flipper.__init__(self, CycleBetween(loop_forever=True, frame=frame, fps=30))
		grid = board.cell_px
		self.rect = pygame.Rect(pos[0] * grid, pos[1] * grid, grid, grid)





if __name__ == '__main__':
	import sys
	sys.exit(TestGame().run())






