"""
Provides classes which are used to do image cycling on a Sprite.
"""

from collections import deque
from legame.resource_manager import ResourceManager
from legame.game import Game


class Flipper:

	@classmethod
	def preload(cls, alpha_channel=True, color_key=None):
		for subclass in Flipper.__subclasses__():
			Game.current.resources.image_set(subclass.__name__, alpha_channel=alpha_channel, color_key=None)


	image_base = None	# base name of this thing's image set. If none, use the class name

	def __init__(self, *cyclers, alpha_channel=True, color_key=None):
		"""
		Initialize the image set used by this Thing, set the current ImageCycle to the first
		ImageCycle object given, and queue up any other ImageCycle given.

		e.g.:

			Flipper.__init__(self, <cycler>, <cycler>, <cycler>)

		See ImageCycle.__init__ for common image cycle options.
		"""
		self._base_image_set = Game.current.resources.image_set(
			self.__class__.__name__ if self.image_base is None else self.image_base,
			alpha_channel=alpha_channel, color_key=color_key
		)
		self._cycler_queue = deque()
		self.queue_cyclers(cyclers)
		self.next_cycler()


	def image_cycle(self, *cyclers):
		"""
		Replaces the current ImageCycle with the first ImageCycle object given, and queues any other
		ImageCycle objects given.

		e.g.:

			thing.image_cycle(<cycler>, <cycler>, <cycler>)

		"""
		self._cycler_queue.clear()
		self.queue_cyclers(cyclers)
		self.next_cycler()


	def queue_cycler(self, cycler):
		"""
		Appends a single ImageCycle object to the queue.
		"""
		cycler.image_set = self._base_image_set if cycler.variant is None else self._base_image_set.variant(cycler.variant)
		self._cycler_queue.append(cycler)


	def queue_cyclers(self, cyclers):
		"""
		Appends a list of ImageCycle objects to the queue.
		"""
		for cycler in cyclers:
			cycler.image_set = self._base_image_set if cycler.variant is None else self._base_image_set.variant(cycler.variant)
		self._cycler_queue.extend(cyclers)


	def update(self):
		"""
		Called from pygame.Sprite, this function updates the "image" property of the sprite.
		If your Sprite uses function as the primary "update" function without modifying it,
		make sure that this function is first in your Sprite's method resolution order (MRO).
		"""
		if self.cycler is None:
			return
		self.image = self.cycler.update()
		if self.cycler.done:
			self.next_cycler()


	def next_cycler(self):
		"""
		Advances to the next ImageCycle in the queue.
		"""
		if len(self._cycler_queue):
			self.cycler = self._cycler_queue.popleft()
			self.image = self.cycler.first_image()
		else:
			self.cycler = None



class ImageCycle:
	"""
	Sets the image on a Sprite to a member of an ImageSet in sequence
	"""

	loop_forever	= False
	loops			= 1			# Number of times to loop through
	fps				= None		# If set, increment image this many frames-per-second

	def __init__(self, variant=None, on_complete=None, **kwargs):
		"""
		When an ImageCycle is queued in a Flipper, it gets a reference to the root of the
		Flipper's ImageSet. Set the variant of the ImageSet to flip using the "variant"
		parameter (string).

		If you would like to be notified when the sequence is complete, pass a function
		reference with the "on_complete" parameter (function reference).

		Other common arguments include:

			loop_forever:		Restart from the beginning after finishing the cycle
			loops:				Number of loops to cycle through, when not "loop_forever"
			fps:				Frames-per-second. The ImageCycle will use the game.fps
								to determine how many frames to skip between flips.

		These vary according to the particular ImageCycle subclass you're using. The ones
		defined in this module include:

			CycleThrough, CycleBetween, and CycleNone

		"""
		self.variant = variant
		self.on_complete_function = on_complete
		for varname, value in kwargs.items(): setattr(self, varname, value)
		self.__updates_per_frame = 1 if self.fps is None \
			else Game.current.fps // self.fps if Game.current is not None \
			else 60 // self.fps
		self.__updates_this_frame = 0
		self._loops_remaining = self.loops
		self.frame = 0
		self.done = False


	def first_image(self):
		"""
		Returns the first image in the set, or the only image in the case of CycleNone.
		"""
		return self.image_set.images[self.frame]


	def update(self):
		"""
		Called from Flipper.update() - advance frame in accordance with fps.
		Returns Image object.
		"""
		if not self.done:
			self.__updates_this_frame += 1
			if self.__updates_this_frame >= self.__updates_per_frame:
				self.__updates_this_frame = 0
				self.advance_frame()
				if self.done and self.on_complete_function:
					self.on_complete_function()
		return self.image_set.images[self.frame]



class CycleNone(ImageCycle):
	"""
	Displays only the first image in the ImageSet
	"""

	def first_image(self):
		self.done = True
		return ImageCycle.first_image(self)


	def advance_frame(self):
		pass



class CycleThrough(ImageCycle):
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



class CycleBetween(ImageCycle):
	"""
	Cycles back and forth through an ImageSet; when at the end, backs up to the beginning
	"""

	def __init__(self, variant=None, **kwargs):
		ImageCycle.__init__(self, variant, **kwargs)
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



