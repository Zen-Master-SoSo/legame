"""
Provides the BroadcastJoiner class, a subclass of Dialog and BroadcastConnector
which returns a Messenger object already connected to another player over the
network.
"""

import importlib
from pygame_dialog import Dialog, Button, Label, ALIGN_LEFT
from time import time
from cable_car.broadcast_connector import BroadcastConnector
from cable_car.messenger import Messenger


class BroadcastJoiner(Dialog, BroadcastConnector):
	"""
	A dialog which allows the user to connect to another player over the network.
	.
	There are two basic methods to use to connect to other computers on the
	network. You can use "broadcast connections", which announce your availability
	using UDP broadcast, or by specifying either "client" or "server" mode in the
	given "options". If neither "client" or "server" is given, broadcast is used
	by default.

	You must pass the name of your selected "transport" to the constuctor. Currently, the
	cable_car Messenger supports two transports; "json" or "byte". The "json" transport is a lot
	easier to implement, but requires more network bandwidth and may be slow for very busy
	network games. In contrast, the "byte" transport is very lightweight, but requires that you
	write message encoding and decoding routines yourself.

	Example:

		joiner = BroadcastJoiner("byte")

	"""

	transport					= "json"
	caption						= "Select a game to join"
	background_color			= (20,20,80)
	background_color_disabled	= (0,0,40)
	foreground_color			= (180,180,255)
	foreground_color_hover		= (20,20,20)
	shutdown_delay				= 0.0


	def __init__(self, options=None):
		"""
		The "options" argument is expected to be a dictionary, the items of which are
		set as attributes of the game during initialization. Some appropriate key/value
		pairs to pass to the __init__ function would be:

			client
			server
			tcp_port
			udp_port
			transport

		... in addition to the common Game class options:

			display_depth

		"""
		Dialog.__init__(self)
		if options is not None:
			for varname, value in options.__dict__.items():
				setattr(self, varname, value)
		module = importlib.import_module("cable_car.%s_messages" % self.transport)
		globals().update({ name: module.__dict__[name] for name in module.__dict__})
		Message.register_messages()
		self.messengers = []
		self.selected_messenger = None
		self._quitting_time = None
		self._address_buttons = []
		for idx in range(4):
			button = Button(
				"",
				font_size = 20,
				padding = 12,
				margin = (2,10),
				foreground_color = self.foreground_color,
				foreground_color_hover = self.foreground_color_hover,
				background_color_disabled = self.background_color_disabled,
				background_color = self.background_color,
				click_handler = self._button_click,
				disabled = True,
				index = idx
			)
			self._address_buttons.append(button)
			self.append(button)
		self._address_buttons[0].margin_top = 10
		self.statusbar = Label(
			"Waiting for other players to appear on the network",
			align = ALIGN_LEFT,
			font_size = 15,
			width = 580,
			foreground_color = self.foreground_color,
			background_color = self.background_color
		)
		self.append(self.statusbar)
		self.on_connect_function = self.on_connect


	def show(self):
		self.initialize_display()
		self._start_connector_threads()
		self._main_loop()
		self.stop_broadcasting()
		self.join_threads()
		if self.__close_thread:
			self.__close_thread.join()
		if self.selected_messenger:
			return
		for msgr in self.messengers:
			msgr.close()


	def on_connect(self, sock):
		"""
		Called when a socket connection is made, creates a new Messenger from new
		socket and appends it to the "messengers" list
		"""
		msgr = Messenger(sock, self.transport)
		# These properties of the Messenger are only relevant when the user
		# is selecting one of many NetworkMessengers, hence are only defined here.
		msgr.remote_user = None
		msgr.remote_hostname = None
		msgr.id_sent = False
		msgr.id_received = False
		msgr.was_invited = False
		msgr.invited_me = False
		msgr.accepted_invitation = False
		self.messengers.append(msgr)


	def loop_end(self):
		"""
		Function called each time through Dialog._main_loop(), updates the buttons,
		statusbar, and messengers.
		"""

		if self._broadcast_enable:
			# Determine what to display on the associated button:
			for idx in range(len(self.messengers)):
				msgr = self.messengers[idx]
				button = self._address_buttons[idx]
				if msgr.closed:
					button.text = "Connection to %s closed" % (msgr.remote_ip)
					button.disabled = True
					continue
				if not msgr.id_sent:
					button.text = "Connected to %s" % (msgr.remote_ip)
					msgr.send(MsgIdentify())
					msgr.id_sent = True
				msgr.xfer()
				# Handle responses from this Messenger
				action = msgr.get()
				if action is not None:
					if isinstance(action, MsgIdentify):
						msgr.id_received = True
						msgr.remote_hostname = action.hostname
						msgr.remote_user = action.username
						button.text = "%s on %s (click to invite)" % (msgr.remote_user, msgr.remote_hostname)
						button.disabled = False
					elif isinstance(action, MsgJoin):
						if msgr.was_invited:
							# Player which was invited accepted invitation - select
							button.text = "%s on %s accepted!" % (msgr.remote_user, msgr.remote_hostname)
							self._select(msgr)
						else:
							msgr.invited_me = True
							button.text = "%s on %s wants to play (click to accept)" % (msgr.remote_user, msgr.remote_hostname)
					else:
						raise Exception("Messenger received an unexpected action: " + action.__class__.__name__)

		else:
			if self._udp_broadcast_exc is None \
				and self._udp_listen_exc is None \
				and self._tcp_listen_exc is None:
				self.statusbar.text = "Connected." if self.selected_messenger else "Cancelled."
			else:
				errors = []
				if self._udp_broadcast_exc: errors.append("Broadcast: " + self._udp_broadcast_exc.__str__())
				if self._udp_listen_exc: errors.append("Listen: " + self._udp_listen_exc.__str__())
				if self._tcp_listen_exc: errors.append("Socket: " + self._tcp_listen_exc.__str__())
				self.statusbar.text = ", ".join(errors)
			if self.shutdown_delay > 0.0:
				if self._quitting_time is None:
					self._quitting_time = time() + self.shutdown_delay
				elif time() >= self._quitting_time:
					self.close()
			else:
				self.close()


	def _button_click(self, button):
		"""
		Click event fired when one of the address listings is clicked.
		"""
		msgr = self.messengers[button.index]
		if msgr.invited_me:
			msgr.send(MsgJoin())
			self._select(msgr)
		elif not msgr.was_invited:
			msgr.send(MsgJoin())
			msgr.was_invited = True
			button.text = "Waiting for %s on %s to accept" % (msgr.remote_user, msgr.remote_hostname)
			button.disabled = True


	def _select(self, messenger):
		"""
		Called when accepting an invitation or the other player accepts an invitation.
		Sets the "selected_messenger" and exits the game joiner.
		"""
		self.selected_messenger = messenger
		self.stop_broadcasting()
		for msgr in self.messengers:
			if msgr is not self.selected_messenger:
				msgr.close()


class ClientServerJoiner(Dialog):


	tcp_port		= 8223		# Port to connect to / listen on
	transport		= "json"	# cable_car transport to use.
	xfer_interval	= 0.125		# Number of seconds between calls to service the messenger
	connect_timeout	= 10.0		# Number of seconds to wait before giving up when connecting

	@classmethod
	def client_connection(cls, tcp_port=8222, transport="json", timeout=10.0):
		connector = LoopbackClient(tcp_port)
		connector.timeout = timeout
		connector.connect()
		if connector.socket is None:
			raise Exception("Could not connect to server")
		return Messenger(connector.socket)


	@classmethod
	def server_connection(cls, tcp_port=8222, transport="json", timeout=10.0):
		connector = LoopbackServer(tcp_port)
		connector.timeout = timeout
		connector.connect()
		if connector.socket is None:
			raise Exception("No clients connected")
		return Messenger(connector.socket)


	def __init__(self, options=None):
		"""
		The "options" argument is expected to be a dictionary, the items of which are
		set as attributes of the game during initialization. Some appropriate key/value
		pairs to pass to the __init__ function would be:

			tcp_port
			udp_port
			transport

		"""
		Dialog.__init__(self)
		if options is not None:
			for varname, value in options.__dict__.items():
				setattr(self, varname, value)
		module = importlib.import_module("cable_car.%s_messages" % self.transport)
		globals().update({ name: module.__dict__[name] for name in module.__dict__})
		Message.register_messages()
		self.messenger = None



if __name__ == '__main__':
	import argparse, logging, sys

	p = argparse.ArgumentParser()
	p.add_argument("--transport", type=str, default="json")
	p.add_argument("--verbose", "-v", action="store_true", help="Show more detailed debug information")
	p.add_argument("--udp-port", type=int, default=8222)
	p.add_argument("--tcp-port", type=int, default=8223)
	p.add_argument("--broadcast", "-b", action="store_true", help="Connect to a remote machine using broadcast discovery.")
	options = p.parse_args()

	logging.basicConfig(
		stream=sys.stdout,
		level=logging.DEBUG if options.verbose else logging.ERROR,
		format="%(relativeCreated)6d [%(filename)24s:%(lineno)3d] %(message)s"
	)

	if options.broadcast:

		joiner = BroadcastJoiner(options)
		joiner.shutdown_delay = 0.5
		joiner.timeout = 0.0 if options.allow_loopback else 15.0	# Allow time to start on remote machine
		joiner.show()

		print("Addresses:")
		print(joiner.addresses())
		print("Messengers:")
		print([messenger.remote_ip for messenger in joiner.messengers])
		print("Selected:")
		print(joiner.selected_messenger.remote_ip if joiner.selected_messenger else None)


	else:

