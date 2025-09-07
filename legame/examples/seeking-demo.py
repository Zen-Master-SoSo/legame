#  legame/examples/seeking-demo.py
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
Demonstrates seeking behavior of the MovingSprite class found in the
"sprite_enhancement" module.
"""
import argparse, logging
import pygame
from pygame import Surface
from pygame.draw import polygon, circle, line
from pygame.sprite import Sprite
from pygame.math import Vector2 as Vector
try:
	from pygame.locals import SRCALPHA, K_q, K_ESCAPE
except ImportError:
	from pygame import SRCALPHA, K_q, K_ESCAPE
from legame import vint
from legame.game import Game, GameState
from legame.sprite_enhancement import MovingSprite


class SeekingDemo(Game):
	"""
	Describe your game class here.
	"""

	fps	= 30

	def __init__ (self, options = None):
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

	def key_down(self, event):
		"""
		Exit game immediately if K_ESCAPE key or "Q" key pressed
		"""
		if event.key in (K_ESCAPE, K_q):
			Game.current.shutdown()

	def quit_event(self, event):
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
	max_turning_speed	= 10

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
		polygon(self.image, self.color, [vint(Vector(p).rotate(self.direction) + self.center_point) \
			for p in self.points])
		self.destination = self.target.position
		self.seek_motion()


if __name__ == '__main__':
	p = argparse.ArgumentParser()
	p.add_argument("--verbose", "-v", action = "store_true", help = "Show more detailed debug information")
	p.epilog = __doc__
	options = p.parse_args()
	logging.basicConfig(
		level = logging.DEBUG if options.verbose else logging.ERROR,
		format = "[%(filename)24s:%(lineno)-4d] %(message)s"
	)

	p.exit(SeekingDemo().run())


#  end legame/examples/seeking-demo.py
