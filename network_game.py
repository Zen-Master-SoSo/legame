"""
Provides the NetworkGame class, a framework for games played over a network.
"""

import importlib, cable_car, traceback
from time import time, sleep
from legame.game import Game, GameState
from legame.joiner import GameJoiner
from legame.exit_states import GSQuit
from cable_car.messenger import Messenger


class NetworkGame(Game):
	"""
	Basic framework for a game to be played over a network. Requires: cable_car.
	.
	There are two basic methods to use to connect to other computers on the
	network. You can use "broadcast connections", which announce your availability
	using UDP broadcast, or by specifying either "client" or "server" mode in the
	given "options". If neither "client" or "server" is given, broadcast is used
	by default.

	Message transport selection is up to you. The current options are "json" and "byte".
	See the cable_car docs for more info on message transports.
	"""

	udp_port		= 8222		# Port to broadcast on
	tcp_port		= 8223		# Port to listen on
	client			= False		# Connect as a client, instead of using udp broadcast
	server			= False		# Connect as a server, instead of using udp broadcast
	transport		= "json"	# cable_car transport to use.
	xfer_interval	= 0.125		# Number of seconds between calls to service the messenger
	connect_timeout	= 10.0		# Number of seconds to wait before giving up when connecting


	def __init__(self, options=None):
		"""
		Network game constructor.
		.

		The "options" argument is expected to be a dictionary, the items of which are
		set as attributes of the game during initialization. Some appropriate key/value
		pairs to pass to the __init__ function would be:

			client
			server
			tcp_port
			udp_port
			transport
			xfer_interval

		... in addition to the common Game class options:

			display_depth
			fps
			fullscreen
			quiet
			resource_dump

		"""
		if options is not None:
			for varname, value in options.__dict__.items():
				setattr(self, varname, value)
		module = importlib.import_module("cable_car.%s_messages" % self.transport)
		globals().update({ name: module.__dict__[name] for name in module.__dict__})
		if self.client:
			self.messenger = Messenger.client_connection(self.tcp_port, self.transport, self.connect_timeout)
		elif self.server:
			self.messenger = Messenger.server_connection(self.tcp_port, self.transport, self.connect_timeout)
		else:
			self.__joiner = GameJoiner(options)
			self.messenger = None


	def run(self):
		if self.messenger is None:
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


