#  legame/examples/alien-herd.py
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
Visual variant of "herd.py" (which demonstrates "neighbor" detection using the
Neighborhood class.)
"""
import argparse, logging
from random import seed, randrange
from legame.examples.herd import HerdDemo, Forager, Predator, GSWatch


class AlienHerdDemo(HerdDemo):

	cells_x			= 16
	cells_y			= 11
	bg_color		= (0,0,14)
	num_foragers	= 120
	num_predators	= 10

	def initial_state(self):
		for i in range(50):
			AienForager(randrange(20, 210), randrange(20, 110), randrange(0, 360))
		for i in range(7):
			AlienPredator(randrange(140, 400), randrange(100, 300), randrange(0, 360))
		return GSWatch()


class AienForager(Forager):
	color				= (60,120,25)
	running_color		= (90,200,45)
	low_speed			= 0.18
	high_speed			= 1.125
	turn_sluggish		= 30
	accel_sluggish		= 44


class AlienPredator(Predator):
	color				= (160,22,16)
	running_color		= (180,52,28)
	eat_color			= (248,20,40)
	low_speed			= 0.3
	high_speed			= 0.95
	turn_sluggish		= 10
	accel_sluggish		= 20


if __name__ == '__main__':
	p = argparse.ArgumentParser()
	p.add_argument("--verbose", "-v", action = "store_true",
		help = "Show more detailed debug information")
	p.epilog = __doc__
	options = p.parse_args()
	logging.basicConfig(
		level = logging.DEBUG if options.verbose else logging.ERROR,
		format = "[%(filename)24s:%(lineno)-4d] %(message)s"
	)

	seed()
	p.exit(AlienHerdDemo().run())


#  end legame/examples/alien-herd.py
