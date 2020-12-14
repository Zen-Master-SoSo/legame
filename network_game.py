"""
Provides the NetworkGame class, a framework for games played over a network.
Message transport selection is up to you. The current options are "json" and "byte".
The the cable_car docs for more info on message transports.
"""

import importlib, cable_car, traceback
from time import time, sleep
from legame.game import Game, GameState
from legame.joiner import GameJoiner
from legame.exit_states import GSQuit
from cable_car.messenger import Messenger


class NetworkGame(Game):

	udp_port		= 8222
	tcp_port		= 8223
	xfer_interval	= 0.125		# Number of seconds between calls to service the messenger


	def __init__(self, transport="json", allow_loopback=False):
		"""
		Network game constructor.
		.

		"transport" may be one of either "json" or "byte". See the cable_car
		documentation for more info on message transports.


		"""
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
		if not self.__joiner.selected_messenger: return 5
		self.messenger = self.__joiner.selected_messenger
		del self.__joiner
		self._next_xfer = time()
		try:
			return Game.run(self)
		except Exception as e:
			traceback.print_exc()
			self.messenger.send(MsgQuit())
			self.messenger.shutdown()
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
	if not Game.current.messenger.closed: Game.current.messenger.send(MsgQuit())
	GSQuit()

GameState.handle_message = _handle_message
GameState.quit = _net_quit


