import random
from pygame import Rect, Surface
from pygame.draw import polygon, circle, line
from pygame.sprite import Sprite
from pygame.math import Vector2 as Vector
from pygame.locals import SRCALPHA, KEYDOWN, QUIT, K_ESCAPE, K_SPACE, K_RETURN, K_q
from legame.game import Game, GameState
from legame.flipper import Flipper, FlipNone, FlipThrough, FlipBetween
from legame.sprite_enhancement import CenteredSprite, MovingSprite, BoxedInSprite
from legame.locals import *


class MyGame(Game):

	fps 				= 30
	caption				= "MyGame"


	def __init__ (self, options=None):
		self.set_resource_dir_from_file(__file__)
		Game.__init__(self, options)


	def initial_background(self, display_size):
		bg = Surface((400, 400))
		bg.fill((0,0,0))
		return bg


	def initial_state(self):
		return EmptyGameState()



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


	def keydown(self, event):
		"""
		Key down event passed to this GameState.
		"event" will contain: key, mod, unicode, scancode
		"""
		if event.key == K_ESCAPE or event.key == K_q:
			Game.current.shutdown()


	def quit(self, event):
		"""
		Event handler called when the user clicks the window's close button.
		event will be empty
		"""
		Game.current.shutdown()


	def keyup(self, event):
		"""
		Key up event passed to this GameState.
		"event" will contain: key, mod
		"""
		pass


	def mousemotion(self, event):
		"""
		Mouse move event passed to this GameState.
		"event" will contain: pos, rel, buttons
		"""
		pass


	def mousebuttondown(self, event):
		"""
		Mouse down event passed to this GameState.
		"event" will contain: pos, button
		"""
		pass


	def mousebuttonup(self, event):
		"""
		Mouse up event passed to this GameState.
		"event" will contain: pos, button
		"""
		pass


	def activeevent(self, event):
		"""
		"event" will contain: gain, state
		"""
		pass


	def joyaxismotion(self, event):
		"""
		Joystick motion event passed to this GameState.
		"event" will contain: instance_id, axis, value
		"""
		pass


	def joyballmotion(self, event):
		"""
		Joystick ball motion event passed to this GameState.
		"event" will contain: instance_id, ball, rel
		"""
		pass


	def joyhatmotion(self, event):
		"""
		Joystick hat motion event passed to this GameState.
		"event" will contain: instance_id, hat, value
		"""
		pass


	def joybuttondown(self, event):
		"""
		Joystick button down event passed to this GameState.
		"event" will contain: instance_id, button
		"""
		pass


	def joybuttonup(self, event):
		"""
		Joystick button up event passed to this GameState.
		"event" will contain: instance_id, button
		"""
		pass


	def videoresize(self, event):
		"""
		Event handler called when the window / display is resized.
		"event" will contain: size, w, h
		"""
		pass


	def videoexpose(self, event):
		"""
		Event handler called when the window is exposed(?)
		"event" will be empty
		"""
		pass


	def videoresize(self, event):
		"""
		Event handler called when the window / display is resized.
		event will contain: size, w, h
		"""
		pass


	def videoexpose(self, event):
		"""
		Event handler called when the window is exposed(?)
		event will be empty
		"""
		pass



class EmptySprite(MovingSprite, Flipper, Sprite):

	def __init__(self, x, y):
		MovingSprite.__init__(self, x, y)
		Flipper.__init__(self, FlipThrough("appear"), FlipNone())
		Sprite.__init__(self, Game.current.sprites)
		Game.current.sprites.change_layer(self, Game.LAYER_PLAYER)




if __name__ == '__main__':
	import argparse, sys, logging

	p = argparse.ArgumentParser()
	p.epilog = """
	Describe your game here.
	"""
	p.add_argument("--quiet", "-q", action="store_true", help="Don't make sound")
	p.add_argument("--verbose", "-v", action="store_true", help="Show more detailed debug information")
	p.add_argument("--resource-dump", "-r", action="store_true", help="Show sound and image resources for debugging")
	options = p.parse_args()
	logging.basicConfig(
		stream=sys.stdout,
		level=logging.DEBUG if options.verbose else logging.ERROR,
		format="[%(filename)24s:%(lineno)3d] %(message)s"
	)

	game = MyGame(options)
	if options.resource_dump:
		Flipper.preload()
		game.resources.dump()
		sys.exit(0)
	else:
		sys.exit(game.run())


