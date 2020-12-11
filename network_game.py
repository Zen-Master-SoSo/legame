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

import importlib
from time import time
from legame3.game import *
from legame3.network_game_joiner import GameJoiner
from cable_car.messenger import Messenger


class NetworkGame(Game):

	udp_port		= 8222
	tcp_port		= 8223
	transport		= "json"
	xfer_interval	= 0.125		# Number of seconds between calls to service the messenger

	allow_loopback	= False


	def __init__(self, transport=None):
		if transport is not None:
			self.transport = transport
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
			Game.run(self)


	def loop_end(self):
		if time() >= self._next_xfer:
			self._next_xfer = time() + self.xfer_interval
			self.messenger.xfer()
			message = self.messenger.get()
			while message is not None:
				if isinstance(message, MsgQuit):
					GSOpponentQuit()
				else:
					self._state.handle_message(message)
				message = self.messenger.get()



# Game states:

class GSOpponentQuit(GSExiting):

	image = "bye-bye.png"

	def enter_state(self):
		Game.current.statusbar.write("%s quit :(" % Game.current.messenger.remote_user)
		ExitAnimation(self.image)


# Dynamically append methods to GameState class which are only used by NetworkGame.
# This greately simplifies code which uses GameState:

def _net_handle_message(self, message):
	pass

def _net_quit(self, event):
	if not Game.current.messenger.closed:
		Game.current.messenger.send(MsgQuit())
	GSExiting()

GameState.handle_message = _net_handle_message
GameState.quit = _net_quit


