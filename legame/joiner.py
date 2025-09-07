#  legame/joiner.py
#
#  Copyright 2020 - 2025 Leon Dionne <ldionne@dridesign.sh.cn>
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#
"""
Provides the BroadcastJoiner class, a subclass of Dialog and BroadcastConnector
which returns a Messenger object already connected to another player over the
network.
"""
import importlib, re, threading
from time import time
from socket import socket, AF_INET, SOCK_DGRAM
from pgdialog import 	Dialog, Button, Label, Textbox, Radio, HorizontalLayout, \
						ALIGN_LEFT, ALIGN_CENTER
from cable_car.broadcast_connector import BroadcastConnector
from cable_car.direct_connect import DirectClient, DirectServer
from cable_car.messenger import Messenger


def get_my_ip():
	sock = socket(AF_INET, SOCK_DGRAM)
	sock.connect(('8.8.8.8', 7))
	return sock.getsockname()[0]


class JoinerDialog(Dialog):
	"""
	Base class of dialog which allows the user to connect to another player over the network.
	"""

	transport					= "json"
	caption						= "Select a game to join"
	background_color			= (20,20,80)
	background_color_disabled	= (0,0,40)
	foreground_color			= (180,180,255)
	foreground_color_hover		= (220,220,255)
	shutdown_delay				= 0.5

	def __init__(self, options = None):
		"""
		The "options" argument is expected to be a dictionary, the items of which are
		set as attributes of the game during initialization. Some appropriate key/value
		pairs to pass to the __init__ function would be:

			client
			server
			tcp_port
			udp_port
			transport

		"""
		if options is not None:
			for varname, value in options.__dict__.items():
				setattr(self, varname, value)
		Dialog.__init__(self)
		module = importlib.import_module("cable_car.%s_messages" % self.transport)
		globals().update({ name: module.__dict__[name] for name in module.__dict__})
		Message.register_messages()
		self.statusbar = Label(
			"",
			align = ALIGN_LEFT,
			font_size = 15,
			width = 540,
			foreground_color = self.foreground_color,
			background_color = self.background_color
		)

	def close(self):
		"""
		Override Dialog.close()
		Turn off "_connect_enable" so that connection threads exit.
		Sets up a pause before closing when "shutdown_delay" is not zero.
		"""
		self._connect_enable = False
		self._quitting_time = time() + self.shutdown_delay
		self.loop_end = self._closing

	def _closing(self):
		"""
		Function which replaces "loop_end" when closing JoinerDialog.
		Inserts a pause before killing the main loop, closing the dialog.
		"""
		if time() >= self._quitting_time:
			self._run_loop = False


class BroadcastJoiner(JoinerDialog, BroadcastConnector):
	"""
	A dialog which allows the user to connect to another player over the network by
	sending UDP broadcast messages and listening for connection attempts from
	machines which have received broadcast packets.

	When a connection is made, user and host name is sent to the remote computer.
	This is displayed on the buttons on this dialog, and the user can select one of
	the remote computers by clicking on one of the buttons.

	This class uses the cable_car Messenger class which allows for two different
	types of transport to be used; "json" or "byte". The "json" transport is a lot
	easier to implement, but requires more network bandwidth and may be slow for
	very busy network games. In contrast, the "byte" transport is very lightweight,
	but requires that you write message encoding and decoding routines yourself.

	The default transport is "json", but this can be overridden by defining a class
	variable in a subclass, or by passing "transport = byte" as an option to the
	__init__ function.

	"""

	def __init__(self, options = None):
		JoinerDialog.__init__(self, options)
		self.messengers = []
		self.messenger = None
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
		self.statusbar.text = "Waiting for other players to appear on the network"
		self.append(self.statusbar)
		self.on_connect_function = self.on_connect

	def show(self):
		self.initialize_display()
		self._start_connector_threads()
		self._main_loop()
		self._connect_enable = False
		self.join_threads()

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

		if self._connect_enable:
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
				message = msgr.get()
				if message is not None:
					if isinstance(message, MsgIdentify):
						msgr.id_received = True
						msgr.remote_hostname = message.hostname
						msgr.remote_user = message.username
						button.text = "%s on %s (click to invite)" % (msgr.remote_user, msgr.remote_hostname)
						button.disabled = False
					elif isinstance(message, MsgJoin):
						if msgr.was_invited:
							# Player which was invited accepted invitation - select
							button.text = "%s on %s accepted!" % (msgr.remote_user, msgr.remote_hostname)
							self._select(msgr)
						else:
							msgr.invited_me = True
							button.text = "%s on %s wants to play (click to accept)" % (msgr.remote_user, msgr.remote_hostname)
					else:
						raise Exception("Messenger received an unexpected message: " + message.__class__.__name__)

		else:
			if self._udp_broadcast_exc is None \
				and self._udp_listen_exc is None \
				and self._tcp_listen_exc is None:
				self.statusbar.text = "Connected." if self.messenger else "Cancelled."
			else:
				errors = []
				if self._udp_broadcast_exc: errors.append("Broadcast: " + self._udp_broadcast_exc.__str__())
				if self._udp_listen_exc: errors.append("Listen: " + self._udp_listen_exc.__str__())
				if self._tcp_listen_exc: errors.append("Socket: " + self._tcp_listen_exc.__str__())
				self.statusbar.text = ", ".join(errors)
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
		Sets the "messenger" and exits the game joiner.
		"""
		self.messenger = messenger
		for msgr in self.messengers:
			if msgr is not self.messenger:
				msgr.close()
		self.close()


class DirectJoiner(JoinerDialog):

	tcp_port			= 8223		# Port to connect to / listen on
	transport			= "json"	# cable_car transport to use.
	timeout				= None		# Absolute limit on how long to wait.

	__connector			= None		# Instance of DirectClient or DirectServer
	__connect_thread	= None		# Connector thread
	__connect_exc		= None		# Exception raised in self.__connector thread
	__connect_failed	= False

	def __init__(self, options = None):
		JoinerDialog.__init__(self, options)
		self.messenger = None
		self.append(HorizontalLayout(
			Radio("mode", "Client",
				foreground_color = self.foreground_color,
				foreground_color_hover = self.foreground_color_hover,
				background_color_disabled = self.background_color_disabled,
				background_color = self.background_color,
				click_handler = self.mode_select
			),
			Radio("mode", "Server",
				foreground_color = self.foreground_color,
				foreground_color_hover = self.foreground_color_hover,
				background_color_disabled = self.background_color_disabled,
				background_color = self.background_color,
				click_handler = self.mode_select
			)
		))
		self.ip_entry = Textbox(get_my_ip(),
			font_size = 32,
			disabled = True,
			align = ALIGN_CENTER
		)
		self.append(self.ip_entry)
		self.start_button = Button("Connect",
			disabled = True,
			foreground_color = self.foreground_color,
			foreground_color_hover = self.foreground_color_hover,
			background_color_disabled = self.background_color_disabled,
			background_color = self.background_color,
			click_handler = self.start
		)
		self.append(self.start_button)
		self.statusbar.text = "Select the mode (client or server)"
		self.append(self.statusbar)

	def show(self):
		self.initialize_display()
		self._main_loop()
		self._connect_enable = False
		if self.__connect_thread: self.__connect_thread.join()

	def mode_select(self, radio):
		if radio.text == "Client":
			self.ip_entry.enabled = True
			self.start_button.enabled = re.match("^[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}$", self.ip_entry.text)
		else:
			self.ip_entry.enabled = False
			self.start_button.enabled = True
			self.ip_entry.text = get_my_ip()

	def start(self, pos):
		if Radio.selected_value("mode") == "Client":
			if re.match("^[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}$", self.ip_entry.text):
				self.disable_widgets()
				self.__connect_thread = threading.Thread(target = self.client_connect)
				self.statusbar.text = "Connecting to %s ..." % self.ip_entry.text
			else:
				self.ip_entry.focus()
				self.statusbar.text = "Enter a valid ip address"
				return
		else:
			self.disable_widgets()
			self.__connect_thread = threading.Thread(target = self.server_connect)
			self.statusbar.text = "Listening for client connection ..."
		self.__connect_thread.start()

	def disable_widgets(self):
		for widget in self.widgets(): widget.disabled = True

	def client_connect(self):
		self.__connect(DirectClient(self.tcp_port, self.ip_entry.text))

	def server_connect(self):
		self.__connect(DirectServer(self.tcp_port, self.ip_entry.text))

	def __connect(self, connector):
		self.__connector = connector
		self.__connector.timeout = self.timeout
		self.__connector.connect()
		if self.__connector.socket is None:
			self.__connect_failed = True
		else:
			self.messenger = Messenger(self.__connector.socket, self.transport)
			self.messenger.id_sent = False
			self.messenger.id_received = False

	def loop_end(self):
		"""
		Function called each time through Dialog._main_loop()
		"""
		if self.messenger:
			if self.messenger.closed:
				self.statusbar.text = "Connection to %s closed" % (self.messenger.remote_ip)
			else:
				if self.messenger.id_sent and self.messenger.id_received:
					self.statusbar.text = "%s at %s connected" % (self.messenger.remote_user, self.messenger.remote_hostname)
					self.close()
				elif not self.messenger.id_sent:
					self.statusbar.text = "Connected to %s" % (self.messenger.remote_ip)
					self.messenger.send(MsgIdentify())
					self.messenger.id_sent = True
				self.messenger.xfer()
				message = self.messenger.get()
				if message is not None:
					if isinstance(message, MsgIdentify):
						self.messenger.id_received = True
						self.messenger.remote_hostname = message.hostname
						self.messenger.remote_user = message.username
					else:
						self.__connector.cancel()
						err = "Messenger received an unexpected message: " + message.__class__.__name__
						logging.error(err)
						self.statusbar.text = err
		elif self.__connect_failed:
			# Only happens when connector thread faults out.
			self.close()


if __name__ == '__main__':
	import argparse, logging

	p = argparse.ArgumentParser()
	p.add_argument("--transport", type = str, default = "json")
	p.add_argument("--verbose", "-v", action = "store_true", help = "Show more detailed debug information")
	p.add_argument("--udp-port", type = int, default = 8222)
	p.add_argument("--tcp-port", type = int, default = 8223)
	p.add_argument("--direct", "-d", action = "store_true", help = "Connect by ip address instead of using udp broadcast discovery.")
	options = p.parse_args()

	logging.basicConfig(
		level = logging.DEBUG if options.verbose else logging.ERROR,
		format = "%(relativeCreated)6d [%(filename)24s:%(lineno)-4d] %(message)s"
	)

	if options.direct:

		joiner = DirectJoiner(options)
		joiner.shutdown_delay = 0.5
		joiner.timeout = 15.0
		joiner.show()

	else:

		joiner = BroadcastJoiner(options)
		joiner.shutdown_delay = 0.5
		joiner.timeout = 15.0
		joiner.show()

		print("Addresses:")
		print(joiner.addresses())
		print("Messengers:")
		print([messenger.remote_ip for messenger in joiner.messengers])

	print("Selected:")
	print(joiner.messenger.remote_ip if joiner.messenger else None)


#  end legame/joiner.py
