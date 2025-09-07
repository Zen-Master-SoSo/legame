#!/usr/bin/python3
#  legame/templates/network-board-game.py
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
try:
	from pygame.locals import K_q, K_ESCAPE
except ImportError:
	from pygame import K_q, K_ESCAPE
from cable_car.json_messages import Message, MsgQuit
from legame.game import Game, GameState, GameStateFinal
from legame.board_game import Cell, GamePiece, GameBoard, BoardGame
from legame.network_game import NetworkGame
from legame.flipper import Flipper, FlipThrough, FlipNone


class MyGame(BoardGame, NetworkGame):

	def __init__ (self, options):
		self.set_resource_dir_from_file(__file__)
		BoardGame.__init__(self, options)
		NetworkGame.__init__(self, options)

	def run(self):
		return NetworkGame.run(self)

	def get_board(self):
		return MyBoard()

	def initial_state(self):
		return EmptyGameState()


class MyBoard(GameBoard):

	columns				= 8
	rows				= 8


class EmptyGameState(GameState):
	"""
	Example GameState subclass.
	Trim out whatever you don't need. All of these functions are included in the
	GameState class.
	"""

	def enter_state(self):
		"""
		Function called when the Game transitions TO this state.
		Any information needed to be passed to this GameState should be passed
		as keyword args to the constructor.
		"""

	def exit_state(self, next_state):
		"""
		Function called when the Game transitions OUT OF this state.
		The "next_state" parameter is the GameState object which will replace this one.
		"""

	def handle_message(self, message):
		"""
		Function called when a message comes over the wire through Game.current.messenger.
		"""
		if isinstance(message, MsgQuit):
			GSQuit(who = "them")

	def key_down(self, event):
		"""
		Key down event passed to this GameState.
		"event" will contain: key, mod, unicode, scancode
		"""
		if event.key in (K_ESCAPE, K_q):
			GSQuit(who = "me")

	def quit_event(self, event):
		"""
		Event handler called when the user clicks the window's close button.
		event will be empty
		"""
		GSQuit(who = "me")

	def key_up(self, event):
		"""
		Key up event passed to this GameState.
		"event" will contain: key, mod
		"""

	def mouse_motion(self, event):
		"""
		Mouse move event passed to this GameState.
		"event" will contain: pos, rel, buttons
		"""

	def mouse_button_down(self, event):
		"""
		Mouse down event passed to this GameState.
		"event" will contain: pos, button
		"""

	def mouse_button_up(self, event):
		"""
		Mouse up event passed to this GameState.
		"event" will contain: pos, button
		"""

	def active_event(self, event):
		"""
		"event" will contain: gain, state
		"""

	def joy_axis_motion(self, event):
		"""
		Joystick motion event passed to this GameState.
		"event" will contain: instance_id, axis, value
		"""

	def joy_ball_motion(self, event):
		"""
		Joystick ball motion event passed to this GameState.
		"event" will contain: instance_id, ball, rel
		"""

	def joy_hat_motion(self, event):
		"""
		Joystick hat motion event passed to this GameState.
		"event" will contain: instance_id, hat, value
		"""

	def joy_button_down(self, event):
		"""
		Joystick button down event passed to this GameState.
		"event" will contain: instance_id, button
		"""

	def joy_button_up(self, event):
		"""
		Joystick button up event passed to this GameState.
		"event" will contain: instance_id, button
		"""

	def video_resize(self, event):
		"""
		Event handler called when the window / display is resized.
		event will contain: size, w, h
		"""

	def video_expose(self, event):
		"""
		Event handler called when the window is exposed(?)
		event will be empty
		"""


class GSQuit(GameStateFinal):

	def enter_state(self):
		if self.who == "me":
			Game.current.messenger.send(MsgQuit())


class MsgAdd(Message):

	def encoded_attributes(self):
		return { "cell" : (self.cell.column, self.cell.row) }

	def decode_attributes(self, attributes):
		self.cell = Game.current.board.rotate(Cell(attributes["cell"][0], attributes["cell"][1]))


class MsgMove(Message):

	def encoded_attributes(self):
		return {
			"cell"			: (self.cell.column, self.cell.row),
			"target_cell"	: (self.target_cell.column, self.target_cell.row)
		}

	def decode_attributes(self, attributes):
		self.cell = Game.current.board.rotate(Cell(attributes["cell"][0], attributes["cell"][1]))
		self.target_cell = Game.current.board.rotate(
			Cell(attributes["target_cell"][0], attributes["target_cell"][1]))


class Piece(GamePiece, Flipper):

	def __init__(self, cell, color):
		self.color = color
		GamePiece.__init__(self, cell, color)
		self.image_folder = "Piece/" + color
		Flipper.__init__(self, FlipThrough("enter"), FlipNone())

	def update(self):
		GamePiece.update(self)
		Flipper.update(self)


if __name__ == '__main__':
	import argparse, sys, logging

	p = argparse.ArgumentParser()
	p.epilog = """
	Describe your game here.
	"""
	p.add_argument("--quiet", "-q", action = "store_true",
		help = "Don't make sound")
	p.add_argument("--verbose", "-v", action = "store_true",
		help = "Show more detailed debug information")
	p.add_argument("--resource-dump", "-r", action = "store_true",
		help = "Show sound and image resources for debugging")
	p.add_argument("--direct", "-d", action = "store_true",
		help = "Connect by ip address instead of using udp broadcast discovery.")
	options = p.parse_args()
	logging.basicConfig(
		level = logging.DEBUG if options.verbose else logging.ERROR,
		format = "[%(filename)24s:%(lineno)-4d] %(message)s"
	)

	game = MyGame(options)
	if options.resource_dump:
		Flipper.preload()
		game.resources.dump()
		sys.exit(0)
	else:
		sys.exit(game.run())


#  end legame/templates/network-board-game.py
