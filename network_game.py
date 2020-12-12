"""Provides the NetworkGame class, a framework for games played over a network.
Message transport selection is up to you!
You must import Message from one of the cable_car message modules, i.e.:

	from cable_car.json_messages import *
	from cable_car.byte_messages import *

Message classes which are included in these files (all take no arguments):
	class MsgIdentify(Message)
	class MsgJoin(Message)
	class MsgRetry(Message)
	class MsgQuit(Message)

"""

import importlib, cable_car
from time import time
from legame.game import Game, GameState
from legame.joiner import GameJoiner
from cable_car.messenger import Messenger


class NetworkGame(Game):

	udp_port		= 8222
	tcp_port		= 8223
	xfer_interval	= 0.125		# Number of seconds between calls to service the messenger


	def __init__(self, transport="json", allow_loopback=False):
		self.transport = transport
		self.allow_loopback = allow_loopback
		if not "Message" in dir():
			try:
				messages = importlib.import_module("cable_car.%s_messages" % self.transport)
			except ImportError:
				raise Exception("%s is not a valid message transport" % self.transport)
			globals().update({name: messages.__dict__[name] for name in [name for name in messages.__dict__]})
		self.__joiner = GameJoiner(self.transport)
		self.__joiner.udp_port = self.udp_port
		self.__joiner.tcp_port = self.tcp_port
		self.__joiner.allow_loopback = self.allow_loopback
		self.messenger = None


	def run(self):
		self.__joiner.show()
		if self.__joiner.selected_messenger:
			self.messenger = self.__joiner.selected_messenger
			self._next_xfer = time()
			del self.__joiner
			return Game.run(self)
		else:
			return 1


	def _end_loop(self):
		"""
		Called at the end of the _main_loop(), this function handles message transfer.
		"""
		self._state.loop_end()
		if time() >= self._next_xfer:
			self._next_xfer = time() + self.xfer_interval
			self.messenger.xfer()
			message = self.messenger.get()
			while message is not None:
				self._state.handle_message(message)
				message = self.messenger.get()



# Dynamically append methods to GameState class which are only used by NetworkGame:

def _handle_message(self, message):
	pass

def _net_quit(self, event):
	if not Game.current.messenger.closed:
		Game.current.messenger.send(MsgQuit())
	GSQuit()

GameState.handle_message = _handle_message
GameState.quit = _net_quit


