"""
Provides classes for easier positioning and moving of sprites.
"""

import math
from pygame import Rect
from pygame.math import Vector2 as Vector
from legame.locals import *



def vector(target):
	"""
	Returns a Vector from the given tuple, Vector, or CenteredSprite.
	Raises ValueError if impossible to convert.
	"""
	if isinstance(target, CenteredSprite): return target.position
	if isinstance(target, Vector): return target
	if isinstance(target, tuple): return Vector(target)
	raise ValueError("Invalid target: %s" % target)



class CenteredSprite:

	height				= 10
	width				= 10


	def __init__(self, x=0.0, y=0.0):
		"""
		CenteredSprite constructor.
		Creates a "rect" property as used by pygame.sprite.Sprite, with the center
		at the x/y position of this Sprite.
		"x" and "y" must be float values which define the position of the object.
		"""
		self.position = Vector(x, y)
		self.rect = Rect(
			self.position.x - self.width / 2.0,
			self.position.y - self.height / 2.0,
			self.width,
			self.height
		)


	@property
	def x(self):
		"""
		Gets the "x" value of this object's positiong vector, relative to the Surface on which this
		object is to be rendered.
		"""
		return self.position.x

	@x.setter
	def x(self, value):
		"""
		Sets the "x" value of this object's positiong vector, relative to the Surface on which this
		object is to be rendered.
		"""
		self.position.x = value


	@property
	def y(self):
		"""
		Gets the "y" value of this object's positiong vector, relative to the Surface on which this
		object is to be rendered.
		"""
		return self.position.y

	@y.setter
	def y(self, value):
		"""
		Sets the "y" value of this object's positiong vector, relative to the Surface on which this
		object is to be rendered.
		"""
		self.position.y = value


	def update_rect(self):
		"""
		Updates the "rect" used by the Sprite class with this CenteredSprite's "position" vector.
		"""
		self.rect.centerx = int(self.position.x)
		self.rect.centery = int(self.position.y)
		return self



class MovingSprite(CenteredSprite):
	"""
	A class compatible with pygame.Sprite which tracks position, motion, rotation in 2d space.
	"""

	max_speed			= 100.0	# Absolute speed limit for this thing
	min_speed			= 0.5	# ...and the slowest its allowed to go
	accel_rate			= 1.0	# Value added to speed each frame when accelerating
	decel_rate			= 1.0	# Value subtracted from speed each frame when decelerating
	turning_speed		= 0.0	# Current turning speed (rotation in degrees per frame)
	max_turning_speed	= 360	# Max degrees per frame this can turn; 360 = unlimited
	destination			= None  # Necessary for seek_motion
	_motion_function	= None	# Function called to move this on Sprite.update()
	_arrival_function	= None	# Function called when destination reached by seeking motion


	def __init__(self, x=0.0, y=0.0, speed=None, direction=None):
		"""
		MovingSprite constructor.
		"x" and "y" must be float values which define the position of the object.
		"speed" must be a float value which sets the magnitude of the motion vector of the object.
		"direction" must be a float value which sets the motion direction of the object in degrees.

		If you would like to use a motion vector made up of x/y values, create a
		"motion" vector with the values you need, and skip this function completely,
		like so:

			class MySprite(MovingSprite):
				def __init__(self):
					CenteredSprite.__init__(self, <x>, <y>)			# Sets Sprite.rect
					self.motion = Vector(<x>, <y>)					# Cartesian
					self._motion_function = self.cartesian_motion	# (example)

		"""
		CenteredSprite.__init__(self, x, y)
		self._motion_function = self.cartesian_motion
		self.motion = Vector()
		if speed is None or direction is None: return
		self.motion.from_polar((speed, direction))


	@property
	def speed(self):
		"""
		Get the "magnitude" of this object's motion vector.
		"""
		return self.motion.magnitude()

	@speed.setter
	def speed(self, value):
		"""
		Sets the "magnitude" of this object's motion vector.
		"""
		try:
			self.motion.scale_to_length(value)
		except ValueError as e:
			self.motion.from_polar((value, 0.0))


	@property
	def direction(self):
		"""
		Gets the screen direction of this MovingSprite in degrees
		"""
		mag, deg = self.motion.as_polar()
		return deg

	@direction.setter
	def direction(self, degrees):
		"""
		Sets the screen direction of this MovingSprite to the given degrees.
		"""
		mag = self.motion.magnitude()
		if mag == 0.0:
			self.motion.from_polar((2.22e-222, degrees))
		else:
			self.motion.from_polar((mag, degrees))


	def update(self):
		"""
		Regular cyclic update task, as called from pygame.Sprite.
		Calls the current move function, which by default is "cartesian_motion".
		"""
		self._motion_function()


	def shift_position(self, x, y):
		"""
		Does a relative cartesian move the position of the object by x, y.
		"""
		self.position.x += x
		self.position.y += y
		self.rect.centerx = int(self.position.x)
		self.rect.centery = int(self.position.y)
		return self


	def set_motion_polar(self, magnitude, degrees):
		"""
		Set the current motion vector from the given magnitude, degrees.
		"""
		self.motion.from_polar((magnitude, degrees))


	def travel_to(self, target, on_arrival=None):
		"""
		High-level command which sets this MovingSprite on a path towards a given target.
		Each subsequent call to "move()" will move the Thing one frame closer to the target.
		When travel is complete, the optional "on_arrival" function will be called.
		"""
		self.destination = vector(target)
		self._motion_function = self.seek_motion
		self._arrival_function = on_arrival
		return self.make_heading()


	def make_heading(self):
		"""
		Sets the initial speed and direction of an object provided a destination
		using the "travel_to()" function.

		The default implementation sets this object's direction to the direction to its
		destination, without taking into consideration turning speed. The speed of this
		MovingSprite is set to it's acceration rate, unless it's already moving faster.

		A true physical moving thing most likely cannot change speed and direction in
		such an immediate fashion, unless the things you hear about "off world" vehicles
		visiting our planet are really true. You're free to model that, I suppose.

		This implementation is sufficient for game pieces such as used in BoardGame,
		but should be overridden in order to create more sophisticated motion.
		"""
		speed = max(self.speed, self.accel_rate)
		self.motion = (self.destination - self.position)
		self.motion.scale_to_length(speed)
		return self


	####################################################################################
	# Move routines which may be called in the "update()" function of the parent Sprite:
	# Various movement methods, called from the "update" method, depending upon the
	# instance and circumstances. The "update" method calls the "_motion_function"
	# which is a reference to one of these methods, or a method in a derived class.
	####################################################################################


	def no_motion(self):
		"""
		A "_motion_function" which does nothing.
		"""
		pass


	def cartesian_motion(self):
		"""
		Moves one frame by adding the x/y values of this MovingSprite's "motion" vector to the
		x/y values of this MovingSprite's "position" vector.
		This is the default "_motion_function".
		"""
		self.position.x += self.motion.x
		self.position.y += self.motion.y
		return self.update_rect()


	def seek_motion(self):
		"""
		One of the "_motion_function" methods, called from "update". This method points
		the sprite towards its current "destination" vector and accelerates towards it,
		decelerating to zero when it approaches.

		This is the move function set in the "travel_to" method.

		This implementation is sufficient for game pieces as used in BoardGame,
		but should be overridden in order to create more sophisticated motion.
		"""
		remaining_distance = (self.destination - self.position).magnitude()
		if remaining_distance <= self.decel_rate:
			self.position = self.destination
			self.rect.centerx = int(self.position.x)
			self.rect.centery = int(self.position.y)
			self.speed = 0.0
			self._motion_function = self.no_motion
			if self._arrival_function:
				self._arrival_function()
		elif remaining_distance <= triangular(self.speed, self.decel_rate):
			# coming up on target_pos; decelerate:
			self.speed = max(self.min_speed, self.speed - self.decel_rate)
		else:
			# still far away from target_pos; accelate towards it:
			self.speed = min(self.max_speed, self.speed + self.accel_rate)
		return self.cartesian_motion()


	####################################################################################
	# High-level movement functions
	####################################################################################


	def turn_towards(self, vector):
		"""
		Turn incrementally towards the given position vector, taking into account this
		MovingSprite's current and max turning speed.
		"""
		self.increment_turning_speed(self.direction_to_vector(vector))
		self.direction += self.turning_speed


	def turn_away_from(self, vector):
		"""
		Turn incrementally away from the given position vector, taking into account
		this MovingSprite's current and max turning speed.
		"""
		self.increment_turning_speed(self.direction_to_vector(vector) + 180)
		self.direction += self.turning_speed


	def increment_turning_speed(self, direction):
		"""
		Incrementally adjust this MovingSprite's "turning_speed" attribute towards or
		away from the given screen direction in degrees, taking into account this
		MovingSprite's current and max turning speed.

		Affects only the "turning_speed" attribute - does NOT change the "motion" vector.
		"""
		desired_turn = turning_degrees(self.direction - direction)
		turn_mag = abs(desired_turn)
		if turn_mag < self.max_turning_speed:
			self.direction = direction
			self.turning_speed = 0.0
		elif abs(self.turning_speed) < self.max_turning_speed:
			self.turning_speed -= math.copysign(self.max_turning_speed, desired_turn)


	####################################################################################
	# Relative position methods:
	####################################################################################

	def distance_to_vector(self, vector):
		"""
		Returns a float - the distance in pixels from this MovingSprite to the given
		position vector.
		"""
		return self.position.distance_to(vector)


	def distance_to_thing(self, thing):
		"""
		Returns a float - the distance in pixels from this MovingSprite to the given
		"thing-like" object.
		"""
		return self.position.distance_to(thing.position)


	def direction_to_vector(self, vector):
		"""
		Returns the world angle in degrees from this MovingSprite's position to the
		given position vector. Returns non-normalized degrees (float).

		If you need a Vector instead of an angle in radians, use Vector subtraction.
		"""
		return (vector - self.position).as_polar()[1]


	def direction_to_thing(self, thing):
		"""
		Returns the world angle in degrees from this MovingSprite's position to the
		given "thing-like" object's position. Returns non-normalized degrees (float).

		If you need a Vector instead of an angle in radians, use Vector subtraction.
		"""
		return (thing.position - self.position).as_polar()[1]


	def angle_to_vector(self, vector):
		"""
		Returns the world angle in degrees from this MovingSprite's position to the
		given position vector. Returns non-normalized degrees (float).

		If you need a Vector instead of an angle in radians, use Vector subtraction.

		Alias of "direction_to_vector".
		"""
		return (vector - self.position).as_polar()[1]


	def angle_to_thing(self, thing):
		"""
		Returns the world angle in degrees from this MovingSprite's position to the
		given "thing-like" object's position. Returns non-normalized degrees (float).

		If you need a Vector instead of an angle in radians, use Vector subtraction.

		Alias of "direction_to_thing".
		"""
		return (thing.position - self.position).as_polar()[1]


	def radians_to_vector(self, vector):
		"""
		Returns the world angle in radians from this MovingSprite's position to the
		given position vector. Returns non-normalized radians (float).

		If you need a Vector, simply subtract this MovingSprite's position from the vector's.
		"""
		return math.radians((vector - self.position).as_polar()[1])


	def radians_to_thing(self, vector):
		"""
		Returns the world angle in radians from this MovingSprite's position to the
		given "thing-like" object's position. Returns non-normalized radians (float).

		If you need a Vector, simply subtract this MovingSprite's position from the vector's.
		"""
		return math.radians((thing.position - self.position).as_polar()[1])


	####################################################################################
	# Status methods:
	####################################################################################

	def is_offscreen(self, screen_rect):
		"""
		Returns one of the "OFFSCREEN_<direction>" constants if this MovingSprite's position
		if outside of the boundaries of the Surface it is to be rendered on.
		"""
		if self.rect.colliderect(screen_rect):
			bits = 0
			if self.position.x < 0:
				bits |= OFFSCREEN_LEFT
			elif self.position.x > screen_rect.width:
				bits |= OFFSCREEN_RIGHT
			if self.position.y < 0:
				bits |= OFFSCREEN_TOP
			elif self.position.y > screen_rect.height:
				bits |= OFFSCREEN_BOTTOM
			return bits
		return 0


	def is_directionless(self):
		"""
		Returns boolean "True" if radians and magnitude of this MovingSprite's motion Vector
		cannot be determined.
		"""
		return self.motion.x == 0 and self.motion.y == 0


	def ns_direction(self):
		"""
		Returns COMPASS_NORTH or COMPASS_SOUTH, depending on if the y-axis of movement is positive or negative
		"""
		return COMPASS_NORTH if self.motion.y < 0 else COMPASS_SOUTH


	def ew_direction(self):
		"""
		Returns COMPASS_EAST or COMPASS_WEST, depending on if the y-axis of movement is positive or negative
		"""
		return COMPASS_WEST if self.motion.x < 0 else COMPASS_EAST


	def __str__(self):
		if self.is_directionless():
			return "<Motionless %s at %.1f / %.1f>" % (type(self).__name__, self.position.x, self.position.y)
		return "<%s at %.1f / %.1f, moving %d degrees at %.1f pixels-per-second>" % \
			(type(self).__name__, self.position.x, self.position.y, self.motion.degrees, self.motion.magnitude())



class BoxedInSprite:
	"""
	A class which can add boundary checking to a MovingSprite.
	"""


	def __init__ (self, boundary):
		"""
		Initialize boundary checking.
		"boundary" is a pygame Rect within which movement is to be constrained.
		Tip: Rect.inflate() can be used to reduce the size of a Rect with a margin around the outside.
		So if you want to restrict movement of a 40px x 40px sprite, such that the outer edges of the
		sprite never leave the screen, you can create a boundary Rect that is 20px (half of the width
		/ height) smaller than the screen Rect using:

			(Screen Rect).inflate(-20)

		"""
		self.boundary = boundary


	def nearest_boundary(self):
		"""
		Determine if near one of the boundary walls.
		Returns None if not near.
		Returns a tuple of (<distance from>, <which wall>) if outside boundary.
		<distance from> is nearest distance to the wall, not distance along MovingSprite's direction
		<which wall> is one of the SIDE_<side> constants defined in locals
		"""
		if self.x < self.boundary.left:
			# Near the west wall
			return (self.x, SIDE_LEFT)
		if self.y < self.boundary.top:
			# Near the north wall
			return (self.y, SIDE_TOP)
		if self.x > self.boundary.right:
			# Near the east wall
			return (self.boundary.right - self.x, SIDE_RIGHT)
		if self.y > self.boundary.bottom:
			# Near the south wall
			return (self.boundary.bottom - self.y, SIDE_BOTTOM)
		return None


	def update(self):
		tup = self.nearest_boundary()
		if tup is not None:
			if tup[1] == SIDE_TOP or tup[1] == SIDE_BOTTOM:
				self.motion.y = - self.motion.y
			else:
				self.motion.x = - self.motion.x
		self.cartesian_motion()



