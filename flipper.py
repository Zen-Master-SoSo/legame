"""
Provides classes which are used to do image cycling on a Sprite.
"""

from collections import deque
from legame.resources import Resources
from legame.game import Game


class Flipper:

	image_base = None	# base name of this thing's image set. If none, use the class name


	@classmethod
	def preload(cls, **kwargs):
		for subclass in Flipper.__subclasses__():
			Game.current.resources.image_set(subclass.__name__, **kwargs)


	def __init__(self, *flippers, **kwargs):
		"""
		Initialize the image set used by this Thing, set the current FlipEffect to the first
		FlipEffect object given, and queue up any other FlipEffect given.

		e.g.:

			Flipper.__init__(self, <flipper>, <flipper>, <flipper>)

		See FlipEffect.__init__ for common image flipper options.
		"""
		self._base_image_set = Game.current.resources.image_set(
			self.__class__.__name__ if self.image_base is None else self.image_base,
			**kwargs
		)
		self._flipper_queue = deque()
		self.queue_flippers(flippers)
		self.next_flipper()


	def flip(self, *flippers):
		"""
		Replaces the current FlipEffect with the first FlipEffect object given, and queues any other
		FlipEffect objects given.

		e.g.:

			thing.flip(<flipper>, <flipper>, <flipper>)

		"""
		self._flipper_queue.clear()
		self.queue_flippers(flippers)
		self.next_flipper()


	def queue_flipper(self, flipper):
		"""
		Appends a single FlipEffect object to the queue.
		"""
		flipper.image_set = self._base_image_set if flipper.variant is None else self._base_image_set.variant(flipper.variant)
		self._flipper_queue.append(flipper)


	def queue_flippers(self, flippers):
		"""
		Appends a list of FlipEffect objects to the queue.
		"""
		for flipper in flippers:
			flipper.image_set = self._base_image_set if flipper.variant is None else self._base_image_set.variant(flipper.variant)
		self._flipper_queue.extend(flippers)


	def update(self):
		"""
		Called from pygame.Sprite, this function updates the "image" property of the sprite.
		If your Sprite uses function as the primary "update" function without modifying it,
		make sure that this function is first in your Sprite's method resolution order (MRO).
		"""
		if self.flipper is None:
			return
		self.image = self.flipper.update()
		if self.flipper.done:
			self.next_flipper()


	def next_flipper(self):
		"""
		Advances to the next FlipEffect in the queue.
		"""
		if len(self._flipper_queue):
			self.flipper = self._flipper_queue.popleft()
			self.image = self.flipper.first_image()
		else:
			self.flipper = None



class FlipEffect:
	"""
	Sets the image on a Sprite to a member of an ImageSet in sequence
	"""

	loop_forever	= False
	loops			= 1			# Number of times to loop through
	fps				= None		# If set, increment image this many frames-per-second
	frame			= None		# May be overriden in the constructor using "frame" kwarg

	def __init__(self, variant=None, on_complete=None, **kwargs):
		"""
		When an FlipEffect is queued in a Flipper, it gets a reference to the root of the
		Flipper's ImageSet. Set the variant of the ImageSet to flip using the "variant"
		parameter (string).

		If you would like to be notified when the sequence is complete, pass a function
		reference with the "on_complete" parameter (function reference).

		Other common arguments include:

			loop_forever:		Restart from the beginning after finishing the cycle
			loops:				Number of loops to cycle through, when not "loop_forever"
			fps:				Frames-per-second. The FlipEffect will use the game.fps
								to determine how many frames to skip between flips.

		These vary according to the particular FlipEffect subclass you're using. The ones
		defined in this module include:

			FlipThrough, FlipBetween, and FlipNone

		"""
		self.variant = variant
		self.on_complete_function = on_complete
		for varname, value in kwargs.items(): setattr(self, varname, value)
		if self.frame is None: self.frame = 0
		self.__updates_per_frame = 1 if self.fps is None \
			else Game.current.fps // self.fps if Game.current is not None \
			else 60 // self.fps
		self._updates_this_frame = 0
		self._loops_remaining = self.loops
		self.done = False


	def first_image(self):
		"""
		Returns the first image in the set, or the only image in the case of FlipNone.
		"""
		return self.image_set.images[self.frame]


	def update(self):
		"""
		Called from Flipper.update() - advance frame in accordance with fps.
		Returns Image object.
		"""
		if not self.done:
			self._updates_this_frame += 1
			if self._updates_this_frame >= self.__updates_per_frame:
				self._updates_this_frame = 0
				self.advance_frame()
				if self.done and self.on_complete_function:
					self.on_complete_function()
		return self.image_set.images[self.frame]



class FlipNone(FlipEffect):
	"""
	Displays only the first image in the ImageSet
	"""

	def first_image(self):
		self.done = True
		return FlipEffect.first_image(self)


	def advance_frame(self):
		pass



class FlipThrough(FlipEffect):
	"""
	Cycles from the start to the end of an ImageSet. If looping, starts again from the beginning,
	otherwise leaves the frame pointer at the end of the image set.
	"""

	def advance_frame(self):
		if self.frame == self.image_set.last_index:
			if self.loop_forever:
				self.frame = 0
			else:
				self._loops_remaining -= 1
				if self._loops_remaining:
					self.frame = 0
				else:
					self.done = True
		else:
			self.frame += 1



class FlipBetween(FlipEffect):
	"""
	Cycles back and forth through an ImageSet; when at the end, backs up to the beginning
	"""

	def __init__(self, variant=None, **kwargs):
		FlipEffect.__init__(self, variant, **kwargs)
		self.__direction = 1


	def advance_frame(self):
		if self.frame == self.image_set.last_index:
			self.__direction = -1
		elif self.frame == 0 and self.__direction < 0:
			self.__direction = 1
			if not self.loop_forever:
				self._loops_remaining -= 1
				self.done = self._loops_remaining == 0
				if self.done:
					return
		self.frame += self.__direction



