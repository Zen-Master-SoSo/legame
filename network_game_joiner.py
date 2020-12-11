"""
Provides the GameJoiner class, a subclass of Dialog and BroadcastConnector which returns a
Messenger object already connected to another player over the network.

Message transport selection is up to you!
You must import Message from one of the cable_car message modules, i.e.:

	from cable_car.json_messages import *
	from cable_car.byte_messages import *

"""

import importlib
from pygame_dialog import Dialog, Button, Label, ALIGN_LEFT
from time import time
from cable_car.broadcast_connector import BroadcastConnector
from cable_car.messenger import Messenger


class GameJoiner(Dialog, BroadcastConnector):
	"""A dialog which allows the user to announce availabiity to play a game over the network and
	invite or accept an invitation from others.
	You must pass the class definition of your selected Message class to the constuctor, i.e.:
		from cable_car.byte_messages import *
		.
		.
		joiner = GameJoiner(Message) # <- no quotes!
	"""

	transport					= "json"
	caption						= "Select a game to join"
	background_color			= (20,20,80)
	background_color_disabled	= (0,0,40)
	foreground_color			= (180,180,255)
	foreground_color_hover		= (20,20,20)
	delay_exit					= False


	def __init__(self, transport=None):
		BroadcastConnector.__init__(self)
		Dialog.__init__(self)
		if not "Message" in dir():
			if transport is not None:
				self.transport = transport
			try:
				messages = importlib.import_module("cable_car.%s_messages" % self.transport)
			except ImportError:
				raise Exception("%s is not a valid message transport" % self.transport)
			globals().update({name: messages.__dict__[name] for name in [name for name in messages.__dict__]})
		Message.register_messages()
		self.messengers = []
		self.selected_messenger = None
		self.quitting_time = None
		self.address_buttons = []
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
			self.address_buttons.append(button)
			self.append(button)
		self.address_buttons[0].margin_top = 10
		self.statusbar = Label(
			" ",
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
		Called when a socket connection is made, creates a new Messenger from new socket and appends it to "messengers"
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
		Function called each time through the _main_loop, updates the buttons, statusbar, and messengers.
		"""

		self.statusbar.text = "Connecting ..." if self.broadcast_enable \
			else "Connected." if self.selected_messenger \
			else "Cancelled."


		if self.selected_messenger:
			if self.delay_exit:
				if self.quitting_time is None:
					self.quitting_time = time() + 1.2
				elif time() >= self.quitting_time:
					return self.close()
			else:
				return self.close()

		# Determine what to display on the associated button:
		for idx in range(len(self.messengers)):
			msgr = self.messengers[idx]
			button = self.address_buttons[idx]
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


if __name__ == '__main__':
	import optparse, sys

	p = optparse.OptionParser()
	p.add_option('--loopback', '-l', action='store_true')
	p.add_option('--transport', type='string', default='json')
	options, arguments = p.parse_args()

	joiner = GameJoiner(options.transport)
	joiner.allow_loopback = options.loopback
	joiner.delay_exit = True
	joiner.timeout = 0.0 if options.loopback else 15.0	# Allow time to start on remote machine
	joiner.show()

	print("Addresses:")
	print(joiner.addresses())
	print("Messengers:")
	print([messenger.remote_ip for messenger in joiner.messengers])
	print("Selected:")
	print(joiner.selected_messenger.remote_ip if joiner.selected_messenger else None)


