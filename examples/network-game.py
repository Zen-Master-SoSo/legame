"""
Demonstrates sending moves over a network.
"""

import random
from legame.game import *
from legame.board_game import *
from legame.flipper import *
from legame.network_game import NetworkGame
from legame.exit_states import GSQuit


class TestGame(BoardGame, NetworkGame):

	xfer_interval	= 0.1		# Number of seconds between calls to service the messenger


	def __init__(self, options=None):
		self.set_resource_dir_from_file(__file__)
		assert os.path.isdir(self.resource_dir)
		BoardGame.__init__(self, options)
		NetworkGame.__init__(self, options)


	def get_board(self):
		return GameBoard(16, 8)


	def initial_state(self):
		global board, statusbar, send, me, my_opponent
		board = Game.current.board
		statusbar = Game.current.statusbar
		send = Game.current.messenger.send
		return GSWhoGoesFirst()



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
		Game.current.set_timeout(self.timeout, 100)


	def timeout(self, args):
		for y in range(board.rows):
			for x in range(board.columns):
				cell = Cell(x, y)
				if board.piece_at(cell) is None:
					Block(cell, Game.current.my_color)
					send(MsgAdd(cell=cell))
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
			board.set_cell(message.cell, Block(message.cell, Game.current.opponent_color))
		elif isinstance(message, MsgQuit):
			GSQuit()
		else:
			raise Exception("Unexpected message: %s" % message)
		GSMyMove()




# Game pieces and other sprites:

class Block(GamePiece, Flipper):

	def __init__(self, cell, color):
		self.image_base = "Block/" + color
		GamePiece.__init__(self, cell, color)
		Flipper.__init__(self, CycleThrough("enter", fps=25), CycleNone())
		self.__glow = None

	def update(self):
		GamePiece.update(self)
		Flipper.update(self)

	def jiggle(self):
		self.cycle(CycleBetween("jiggle", loops=11, fps=30), CycleNone())
		return self

	def glow(self):
		self.__glow = Glow(self.cell)
		return self

	def unglow(self):
		if self.__glow:
			self.__glow.kill()
			self.__glow = None
		return self



class Glow(Flipper, pygame.sprite.Sprite):

	def __init__(self, cell, frame=0):
		self.cell = cell
		pygame.sprite.Sprite.__init__(self, Game.current.sprites)
		Game.current.sprites.change_layer(self, Game.LAYER_BELOW_PLAYER)
		Flipper.__init__(self, CycleBetween(loop_forever=True, frame=frame, fps=30))
		self.rect = self.cell.get_rect()





if __name__ == '__main__':
	import argparse, logging, sys

	p = argparse.ArgumentParser()
	p.epilog = "Demonstrates network game functions."
	p.add_argument("--transport", type=str, default="json")
	p.add_argument("--quiet", "-q", action="store_true", help="Don't make sound")
	p.add_argument("--verbose", "-v", action="store_true", help="Show more detailed debug information")
	p.add_argument("--direct", "-d", action="store_true", help="Connect to a remote machine by ip address instead of using udp broadcast discovery.")
	options = p.parse_args()

	logging.basicConfig(
		stream=sys.stdout,
		level=logging.DEBUG if options.verbose else logging.ERROR,
		format="[%(filename)24s:%(lineno)3d] %(message)s"
	)


	if options.transport == "json":
		from cable_car.json_messages import Message, MsgQuit

		class MsgAdd(Message):

			def encoded_attributes(self):
				return { "cell" : (self.cell.column, self.cell.row) }


			def decode_attributes(self, attributes):
				self.cell = Cell(*attributes["cell"])


			def rotate(self):
				self.cell = board.rotate(self.cell)
				return self


		class MsgPickAColor(Message):

			def __init__(self):
				self.color = random.choice(["r", "g", "b"])
				self.number = random.randrange(0,1000)


	else:
		from cable_car.byte_messages import Message, MsgQuit


		class MsgAdd(Message):
			code = 0x8

			def encode(self):
				"""
				Encode column, row:
				"""
				return bytearray([self.cell.column, self.cell.row])


			def decode(self, msg_data):
				"""
				Read column, row from message data.
				"""
				self.cell = Cell(msg_data[0], msg_data[1])


			def rotate(self):
				self.cell = board.rotate(self.cell)
				return self


		class MsgPickAColor(Message):
			code = 0x9

			def __init__(self):
				self.color = random.choice(["r", "g", "b"])
				self.number = random.randrange(0,256)


			def encode(self):
				"""
				Encode color, number
				"""
				return bytearray([self.number]) + self.color.encode("ASCII")


			def decode(self, msg_data):
				"""
				Read color and number from message data.
				"""
				self.number, self.color = msg_data[0], msg_data[1:].decode()




	sys.exit(TestGame(options).run())





