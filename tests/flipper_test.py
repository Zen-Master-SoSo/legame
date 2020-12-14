import pytest, os
import legame
from legame.flipper import *


@pytest.fixture(autouse=True)
def thing():
	FakeGame()
	return Block()


class FakeGame:
	fps	= 30
	def __init__(self):
		Game.current = self
		examples = os.path.join(os.path.dirname(legame.__file__), "examples")
		if not os.path.isdir(examples):
			raise NotADirectoryError(examples)
		self.resource_dir = os.path.join(os.path.abspath(examples), "resources")
		if not os.path.isdir(self.resource_dir):
			raise NotADirectoryError(self.resource_dir)
		self.resources = Resources(self.resource_dir)
		self.resources.resource_dump = True


class Block(Flipper):
	image_base	= "Block/r"
	def __init__(self):
		Flipper.__init__(self, CycleThrough("enter"))


def test_cycle_through_once(thing):
	assert isinstance(thing.cycler, CycleThrough)
	assert thing.cycler.loop_forever == False
	assert thing.cycler.loops == 1
	assert thing.image == thing.cycler.image_set.images[0]
	for frame in [0, 1, 2]:
		assert thing.cycler.frame == frame
		thing.update()
	assert thing.cycler is None


def test_cycle_through_twice(thing):
	thing.cycle(CycleThrough("enter", loops=2))
	assert thing.cycler.loop_forever == False
	assert(thing.cycler.loops == 2)
	for frame in [0, 1, 2, 0, 1, 2]:
		assert thing.cycler.frame == frame
		thing.update()
	assert thing.cycler is None


def test_between_through_once(thing):
	thing.cycle(CycleBetween("jiggle"))
	assert isinstance(thing.cycler, CycleBetween)
	assert thing.cycler.loop_forever == False
	assert thing.cycler.loops == 1
	for frame in [0, 1, 2, 1, 0]:
		assert thing.cycler.frame == frame
		thing.update()
	assert thing.cycler is None


def test_cycle_between_twice(thing):
	thing.cycle(CycleBetween("jiggle", loops=2))
	assert thing.cycler.loop_forever == False
	assert(thing.cycler.loops == 2)
	assert(thing.image == thing.cycler.image_set.images[0])
	for frame in [0, 1, 2, 1, 0, 1, 2, 1, 0]:
		assert thing.cycler.frame == frame
		thing.update()
	assert thing.cycler is None


def test_cycle_through_loop_forever(thing):
	thing.cycle(CycleThrough("enter", loop_forever=True))
	assert thing.cycler.loop_forever == True
	assert thing.cycler.frame == 0
	for frame in [0, 1, 2, 0, 1, 2, 0, 1, 2, 0, 1, 2, 0, 1, 2]:
		assert thing.cycler.frame == frame
		thing.update()


def test_two_cycles_queued(thing):
	thing.cycle(CycleBetween("jiggle"), CycleThrough("enter"))
	assert(thing.cycler.__class__.__name__ == "CycleBetween")
	assert thing.cycler.loop_forever == False
	assert thing.cycler.loops == 1
	assert thing.cycler.frame == 0
	for frame in [0, 1, 2, 1, 0]:
		assert thing.cycler.frame == frame
		thing.update()
	assert(thing.cycler.__class__.__name__ == "CycleThrough")
	assert thing.cycler.loop_forever == False
	assert thing.cycler.loops == 1
	assert thing.cycler.frame == 0
	for frame in [0, 1, 2]:
		assert thing.cycler.frame == frame
		thing.update()
	assert thing.cycler is None


def test_starting_frame(thing):
	thing.cycle(CycleBetween("jiggle", loop_forever=True, frame=2, fps=30))
	assert thing.cycler.loop_forever == True
	assert thing.cycler.frame == 2




