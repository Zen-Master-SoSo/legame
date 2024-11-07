#!/usr/bin/python3
from pygame import Rect
from pygame.sprite import Sprite
from legame.game import *
from legame.board_game import *
from legame.network_game import NetworkGame
from legame.flipper import *
from legame.exit_states import *
from cable_car.json_messages import *



class MyGame(BoardGame, NetworkGame):


	def __init__ (self, options):
		self.set_resource_dir_from_file(__file__)
		BoardGame.__init__(self, options)
		NetworkGame.__init__(self, options)


	def run(self):
		return NetworkGame.run(self)


	def get_board(self):
		return ColorwarsBoard()


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
		Any information needed to be passed to this GameState should be passed as keyword args to the constructor.
		"""
		pass


	def exit_state(self, next_state):
		"""
		Function called when the Game transitions OUT OF this state.
		The "next_state" parameter is the GameState object which will replace this one.
		"""
		pass


	def handle_message(self, message):
		"""
		Function called when a message comes over the wire through Game.current.messenger.
		"""
		if isinstance(message, MsgQuit):
			GSQuit(who = "them")


	def _evt_keydown(self, event):
		"""
		Key down event passed to this GameState.
		"event" will contain: key, mod, unicode, scancode
		"""
		if event.key == K_ESCAPE or event.key == K_q:
			GSQuit(who = "me")


	def _evt_quit(self, event):
		"""
		Event handler called when the user clicks the window's close button.
		event will be empty
		"""
		GSQuit(who = "me")


	def _evt_keyup(self, event):
		"""
		Key up event passed to this GameState.
		"event" will contain: key, mod
		"""
		pass


	def _evt_mousemotion(self, event):
		"""
		Mouse move event passed to this GameState.
		"event" will contain: pos, rel, buttons
		"""
		pass


	def _evt_mousebuttondown(self, event):
		"""
		Mouse down event passed to this GameState.
		"event" will contain: pos, button
		"""
		pass


	def _evt_mousebuttonup(self, event):
		"""
		Mouse up event passed to this GameState.
		"event" will contain: pos, button
		"""
		pass


	def _evt_activeevent(self, event):
		"""
		"event" will contain: gain, state
		"""
		pass


	def _evt_joyaxismotion(self, event):
		"""
		Joystick motion event passed to this GameState.
		"event" will contain: instance_id, axis, value
		"""
		pass


	def _evt_joyballmotion(self, event):
		"""
		Joystick ball motion event passed to this GameState.
		"event" will contain: instance_id, ball, rel
		"""
		pass


	def _evt_joyhatmotion(self, event):
		"""
		Joystick hat motion event passed to this GameState.
		"event" will contain: instance_id, hat, value
		"""
		pass


	def _evt_joybuttondown(self, event):
		"""
		Joystick button down event passed to this GameState.
		"event" will contain: instance_id, button
		"""
		pass


	def _evt_joybuttonup(self, event):
		"""
		Joystick button up event passed to this GameState.
		"event" will contain: instance_id, button
		"""
		pass


	def _evt_videoresize(self, event):
		"""
		Event handler called when the window / display is resized.
		"event" will contain: size, w, h
		"""
		pass


	def _evt_videoexpose(self, event):
		"""
		Event handler called when the window is exposed(?)
		"event" will be empty
		"""
		pass


	def _evt_videoresize(self, event):
		"""
		Event handler called when the window / display is resized.
		event will contain: size, w, h
		"""
		pass


	def _evt_videoexpose(self, event):
		"""
		Event handler called when the window is exposed(?)
		event will be empty
		"""
		pass



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
		self.target_cell = Game.current.board.rotate(Cell(attributes["target_cell"][0], attributes["target_cell"][1]))



class Piece(GamePiece, Flipper):

	def __init__(self, cell, color):
		self.color = color
		GamePiece.__init__(self, cell, color)
		self.image_folder = "Piece/" + color
		Flipper.__init__(self, CycleThrough("enter"), CycleNone())


	def update(self):
		GamePiece.update(self)
		Flipper.update(self)



if __name__ == '__main__':
	import argparse, sys, logging

	p = argparse.ArgumentParser()
	p.epilog = """
	Describe your game here.
	"""
	p.add_argument("--quiet", "-q", action="store_true", help="Don't make sound")
	p.add_argument("--verbose", "-v", action="store_true", help="Show more detailed debug information")
	p.add_argument("--resource-dump", "-r", action="store_true", help="Show sound and image resources for debugging")
	p.add_argument("--direct", "-d", action="store_true", help="Connect by ip address instead of using udp broadcast discovery.")
	options = p.parse_args()
	logging.basicConfig(
		stream=sys.stdout,
		level=logging.DEBUG if options.verbose else logging.ERROR,
		format="[%(filename)24s:%(lineno)-4d] %(message)s"
	)

	game = MyGame(options)
	if options.resource_dump:
		Flipper.preload()
		game.resources.dump()
		sys.exit(0)
	else:
		sys.exit(game.run())

