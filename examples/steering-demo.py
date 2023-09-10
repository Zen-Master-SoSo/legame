"""
Simple demo which points an arrow at the mouse cursor.
"""

import random, pygame
from pygame import Rect, Surface
from pygame.draw import polygon, circle, line
from pygame.sprite import Sprite
from pygame.math import Vector2 as Vector
from pygame.locals import SRCALPHA, K_ESCAPE, K_q
from legame.game import Game, GameState
from legame.flipper import Flipper, FlipNone, FlipThrough, FlipBetween
from legame.sprite_enhancement import CenteredSprite, MovingSprite, BoxedInSprite
from legame.locals import *


class SteeringDemo(Game):
	"""
	Describe your game class here.
	"""

	fps	= 30

	def __init__ (self, options=None):
		self.set_resource_dir_from_file(__file__)
		Game.__init__(self, options)

	def initial_background(self, display_size):
		bg = Surface((400, 400))
		bg.fill((0,0,0))
		return bg

	def initial_state(self):
		return ChaseState()



class ChaseState(GameState):

	def __init__ (self):
		pygame.mouse.set_visible(False)
		cx, cy = Game.current.screen_rect.center
		mx, my = pygame.mouse.get_pos()
		Chaser(cx, cy, Mouse(mx, my))

	def _evt_keydown(self, event):
		"""
		Exit game immediately if K_ESCAPE key or "Q" key pressed
		"""
		if event.key == K_ESCAPE or event.key == K_q:
			Game.current.shutdown()

	def _evt_quit(self, event):
		Game.current.shutdown()



class Mouse(MovingSprite, Sprite):

	height	= 18
	width	= 18

	def __init__(self, x, y):
		MovingSprite.__init__(self, x, y)
		Sprite.__init__(self, Game.current.sprites)
		Game.current.sprites.change_layer(self, Game.LAYER_ABOVE_PLAYER)
		self.color = pygame.Color("yellow")

	def update(self):
		self.position = Vector(pygame.mouse.get_pos())
		self.image = Surface(self.rect.size, SRCALPHA)
		circle(self.image, self.color, (9,9), 9, 1)
		line(self.image, self.color, (9,0), (9, 18))
		line(self.image, self.color, (0,9), (18, 9))
		self.update_rect()



class Chaser(MovingSprite, Sprite):

	height				= 24
	width				= 24
	max_turning_speed	= 6

	def __init__(self, x, y, mouse):
		MovingSprite.__init__(self, x, y)
		Sprite.__init__(self, Game.current.sprites)
		Game.current.sprites.change_layer(self, Game.LAYER_PLAYER)
		self.target = mouse
		self.color = pygame.Color("white")
		self.points = [
			(12, 0),
			(-12, 10),
			(-4, 0),
			(-12, -10)
		]
		self.center_point = Vector(12, 12)


	def update(self):
		self.turn_towards(self.target.position)
		self.image = Surface(self.rect.size)
		rot = lambda point: Vector(point).rotate(self.direction) + self.center_point
		polygon(self.image, self.color, [rot(p) for p in self.points])
		MovingSprite.update(self)




if __name__ == '__main__':
	import sys
	sys.exit(SteeringDemo().run())



