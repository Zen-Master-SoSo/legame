import random
from pygame import Rect, Surface
from pygame.draw import polygon, circle, line
from pygame.sprite import Sprite
from pygame.math import Vector2 as Vector
from pygame.locals import SRCALPHA, KEYDOWN, QUIT, K_ESCAPE, K_SPACE, K_RETURN, K_q
from legame.game import Game, GameState
from legame.flipper import Flipper, CycleNone, CycleThrough, CycleBetween
from legame.sprite_enhancement import CenteredSprite, MovingSprite, BoxedInSprite
from legame.locals import *


class EmptyGame(Game):
	"""
	Describe your game class here.
	"""

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


	def activeevent(self, event):
		"""
		event will contain: gain, state
		"""
		pass


	def keydown(self, event):
		"""
		Exit game immediately if K_ESCAPE key or "Q" key pressed
		event will contain: key, mod, unicode, scancode
		"""
		if event.key == K_ESCAPE or event.key == K_q:
			Game.current.shutdown()

	def keyup(self, event):
		"""
		Key up event passed to this GameState.
		event will contain: key, mod
		"""
		pass


	def mousemotion(self, event):
		"""
		Mouse move event passed to this GameState.
		event will contain:	pos, rel, buttons
		"""
		pass


	def mousebuttondown(self, event):
		"""
		Mouse down event passed to this GameState.
		event will contain:	pos, button
		"""
		pass


	def mousebuttonup(self, event):
		"""
		Mouse up event passed to this GameState.
		event will contain: pos, button
		"""
		pass


	def joyaxismotion(self, event):
		"""
		Joystick motion event passed to this GameState.
		event will contain:	instance_id, axis, value
		"""
		pass


	def joyballmotion(self, event):
		"""
		Joystick ball motion event passed to this GameState.
		event will contain:	instance_id, ball, rel
		"""
		pass


	def joyhatmotion(self, event):
		"""
		Joystick hat motion event passed to this GameState.
		event will contain: instance_id, hat, value
		"""
		pass


	def joybuttondown(self, event):
		"""
		Joystick button down event passed to this GameState.
		event will contain: instance_id, button
		"""
		pass


	def joybuttonup(self, event):
		"""
		Joystick button up event passed to this GameState.
		event will contain:	instance_id, button
		"""
		pass


	def quit(self, event):
		"""
		Event handler called when the user clicks the window's close button.
		event will be empty
		"""
		Game.current.shutdown()


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




class EmptySprite(MovingSprite, Sprite):

	def __init__(self, x, y):
		MovingSprite.__init__(x, y)
		Sprite.__init__(self, Game.current.sprites)
		Game.current.sprites.change_layer(self, Game.LAYER_PLAYER)





if __name__ == '__main__':
	import sys
	sys.exit(EmptyGame().run())



