#  legame/examples/herd.py
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
Demonstrates "neighbor" detection using the Neighborhood class
"""
import argparse, logging
from random import seed, randrange, uniform
from pygame.sprite import Sprite
from pygame import Rect, Surface
from pygame.draw import circle
try:
	from pygame.locals import SRCALPHA, K_q, K_ESCAPE
except ImportError:
	from pygame import SRCALPHA, K_q, K_ESCAPE
from legame.game import Game, GameState
from legame.sprite_enhancement import MovingSprite, BoxedInSprite
from legame.neighbors import Neighborhood, Neighbor
from legame import	SIDE_LEFT, SIDE_TOP, SIDE_RIGHT, SIDE_BOTTOM, \
					DEGREES_SOUTHEAST, DEGREES_NORTHEAST, DEGREES_NORTHWEST, DEGREES_SOUTHWEST


class HerdDemo(Game, Neighborhood):

	cells_x			= 12
	cells_y			= 8
	cell_width		= 60
	cell_height		= 60
	bg_color		= (240,230,140)
	num_foragers	= 60
	num_predators	= 7

	def __init__ (self):
		global game, neighborhood
		self.set_resource_dir_from_file(__file__)
		self.quiet = True
		Game.__init__(self)
		self.rect = Rect(0, 0, self.cell_width * self.cells_x, self.cell_width * self.cells_y)
		neighborhood = Neighborhood(self.rect.inflate(-30, -30), self.cells_x, self.cells_y)
		game = self

	def initial_background(self, display_size):
		bg = Surface(self.rect.size)
		bg.fill(self.bg_color)
		return bg

	def initial_state(self):
		r = neighborhood.rect
		midleft, midtop = neighborhood.rect.center
		for i in range(self.num_foragers):
			Forager(
				randrange(r.left, midleft),
				randrange(r.top, midtop),
				randrange(0, 360)
			)
		for i in range(self.num_predators):
			Predator(
				randrange(midleft, r.right),
				randrange(midtop, r.bottom),
				randrange(0, 360)
			)
		return GSWatch()

	def _end_loop(self):
		neighborhood.notify_sprites()
		self._state.loop_end()


class GSWatch(GameState):

	def key_down(self, event):
		"""
		Exit game immediately if K_ESCAPE key pressed
		"""
		if event.key in (K_ESCAPE, K_q):
			game.shutdown()

	def quit_event(self, event):
		"""
		Event handler called when the user clicks the window's close button.
		event will be empty
		"""
		game.shutdown()


class Animal(Neighbor, BoxedInSprite, MovingSprite, Sprite):

	height				= 8
	width				= 8

	def __init__(self, x, y, direction):
		Sprite.__init__(self, game.sprites)
		MovingSprite.__init__(self, x, y, self.low_speed, direction)
		BoxedInSprite.__init__(self, game.screen_rect.inflate(-20, -20))
		neighborhood.observe(self)
		self._normal_image = self.make_image(self.color)
		self._bright_image = self.make_image(self.running_color)
		self._accel = (self.high_speed - self.low_speed) / self.accel_sluggish
		self._decel = self._accel * 0.27
		self.max_turning_speed = 90 / self.turn_sluggish
		self._turn_min = -self.max_turning_speed
		self._turn_max = self.max_turning_speed
		self._nearest_animal = None
		self._nearest_animal_distance = None

	def make_image(self, color):
		surf = Surface((8,8), SRCALPHA)
		circle(surf, color, (4, 4), 4)
		return surf

	def boundary_check(self):
		"""
		Calls MovingSprite.cartesian_motion after boundary checking
		"""
		tup = self.nearest_boundary()
		if tup is not None:
			if tup[1] == SIDE_TOP:
				self.direction = DEGREES_SOUTHEAST if self.motion.x > 0 else DEGREES_SOUTHWEST
			elif tup[1] == SIDE_BOTTOM:
				self.direction = DEGREES_NORTHEAST if self.motion.x > 0 else DEGREES_NORTHWEST
			if tup[1] == SIDE_RIGHT:
				self.direction = DEGREES_SOUTHWEST if self.motion.y > 0 else DEGREES_NORTHWEST
			elif tup[1] == SIDE_LEFT:
				self.direction = DEGREES_SOUTHEAST if self.motion.y > 0 else DEGREES_NORTHEAST
			self.turning_speed = 0
		self.cartesian_motion()

	def kill(self):
		neighborhood.ignore(self)
		Sprite.kill(self)


class Forager(Animal):

	color				= (60,120,25)
	running_color		= (90,200,45)
	low_speed			= 0.25
	high_speed			= 1.33
	turn_sluggish		= 24
	accel_sluggish		= 44

	def notice(self, neighbor):
		if isinstance(neighbor, Predator):
			d = self.distance_to_thing(neighbor)
			if self._nearest_animal is None or d < self._nearest_animal_distance:
				self._nearest_animal = neighbor
				self._nearest_animal_distance = d

	def update(self):
		"""
		Default "update" function.
		"""
		if self._nearest_animal is None:
			self.image = self._normal_image
			self.speed = max(self.low_speed, self.speed - self._decel)
			self.turning_speed = uniform(self._turn_min, self._turn_max)
		else:
			self.image = self._bright_image
			self.turn_away_from(self._nearest_animal.position)
			self.speed = min(self.high_speed, self.speed + self._accel)
		self.boundary_check()
		self.cartesian_motion()
		self._nearest_animal = None


class Predator(Animal):

	color				= (140,42,16)
	running_color		= (180,72,28)
	eat_color			= (248,20,40)
	low_speed			= 0.3
	high_speed			= 0.88
	turn_sluggish		= 6
	accel_sluggish		= 14

	max_vigor			= 600
	tire_limit			= 50
	rested_limit		= 400
	eat_frames			= 240

	def __init__(self, x, y, direction):
		Animal.__init__(self, x, y, direction)
		self._eat_image = self.make_image(self.eat_color)
		self._vigor = 400
		self._tired = False
		self.update = self.hunting

	def notice(self, neighbor):
		if isinstance(neighbor, Forager):
			d = self.distance_to_thing(neighbor)
			if self._nearest_animal is None or d < self._nearest_animal_distance:
				self._nearest_animal = neighbor
				self._nearest_animal_distance = d

	def cartesian_motion(self):
		self._nearest_animal = None
		super().cartesian_motion()

	def hunting(self):
		if self._nearest_animal and self._nearest_animal.alive():
			self.image = self._bright_image
			if self._nearest_animal_distance < 4:
				#print("hunting -> kill_prey -> catching  vigor: %d" % self._vigor)
				self.kill_prey()
			else:
				self.image = self._bright_image
				self.turn_towards(self._nearest_animal.position)
				self.speed = min(self.high_speed, self.speed + self._accel)
				self._vigor -= 1
				#print("hunting -> chasing  vigor: %d" % self._vigor)
				self.update = self.chasing
		else:
			self.image = self._normal_image
			self.speed = max(self.low_speed, self.speed - self._decel)
			self.turning_speed = uniform(self._turn_min, self._turn_max)
			self.boundary_check()
		self.cartesian_motion()

	def chasing(self):
		self.image = self._bright_image
		if self._nearest_animal and self._nearest_animal.alive():
			if self._nearest_animal_distance < 4:
				#print("chasing -> kill_prey -> catching  vigor: %d" % self._vigor)
				self.kill_prey()
			elif self._vigor < self.tire_limit:
				self.turning_speed = 0.0
				#print("chasing -> going_to_rest  vigor: %d" % self._vigor)
				self.update = self.going_to_rest
			else:
				self.turn_towards(self._nearest_animal.position)
				self.speed = min(self.high_speed, self.speed + self._accel)
				self._vigor -= 1
		else:
			#print("chasing -> hunting  vigor: %d" % self._vigor)
			self.update = self.hunting
		self.cartesian_motion()

	def kill_prey(self):
		self._nearest_animal.kill()
		self.turning_speed = 0.0
		self.speed = max(0.0, self.speed - self._decel)
		self.update = self.catching

	def catching(self):
		self.image = self._eat_image
		self.speed = max(0.0, self.speed - self._decel)
		if self.speed == 0.0:
			#print("catching -> eating  vigor: %d" % self._vigor)
			self.update = self.eating
			self.eat_frames_countdown = self.eat_frames
		self.cartesian_motion()

	def eating(self):
		self._vigor = max(self.max_vigor, self._vigor + 2)
		self.eat_frames_countdown -= 1
		if self.eat_frames_countdown <= 0:
			#print("eating -> hunting  vigor: %d" % self._vigor)
			self.update = self.hunting

	def going_to_rest(self):
		self.speed -= self._decel
		self.cartesian_motion()
		if self.speed <= self._decel:
			self.speed = 0.0
			#print("going_to_rest -> resting  vigor: %d" % self._vigor)
			self.update = self.resting

	def resting(self):
		self._vigor += 1
		if self._vigor > self.rested_limit:
			#print("resting -> hunting  vigor: %d" % self._vigor)
			self.update = self.hunting


if __name__ == '__main__':
	p = argparse.ArgumentParser()
	p.add_argument("--verbose", "-v", action = "store_true", help = "Show more detailed debug information")
	p.epilog = __doc__
	options = p.parse_args()
	logging.basicConfig(
		level = logging.DEBUG if options.verbose else logging.ERROR,
		format = "[%(filename)24s:%(lineno)-4d] %(message)s"
	)

	seed()
	p.exit(HerdDemo().run())

#  legame/examples/herd.py
