"""
Visual variant of "herd.py" (which demonstrates "neighbor" detection using the
Neighborhood class.)
"""

from .herd import *

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
	import sys
	sys.exit(AlienHerdDemo().run())


