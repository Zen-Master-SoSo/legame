import pytest, os
import legame3
from legame3.game import Game
from legame3.resource_manager import *


@pytest.fixture(autouse=True)
def rm():
	return FakeGame().resources


class FakeGame:
	def __init__(self):
		Game.current = self
		examples = os.path.join(os.path.dirname(legame3.__file__), "examples")
		if not os.path.isdir(examples):
			raise NotADirectoryError(examples)
		self.resource_dir = os.path.join(os.path.abspath(examples), "resources")
		if not os.path.isdir(self.resource_dir):
			raise NotADirectoryError(self.resource_dir)
		self.resources = ResourceManager(self.resource_dir, True)


def test_basic_dirty(rm):
	assert rm.dirty == False
	assert rm.resource_dump == True
	assert os.path.isfile(rm.image("bye-bye.png"))
	assert rm.dirty == True


def test_sound_loader(rm):
	assert os.path.isfile(rm.sound("bust.wav"))


def test_image_set(rm):
	imgset = rm.image_set("Block")
	assert(isinstance(imgset, ImageSet))
	assert(imgset.count == 0)


def test_subset(rm):
	imgset = rm.image_set("Block")
	imgset = imgset["b"]
	assert(isinstance(imgset, ImageSet))
	assert(imgset.count == 1)
	assert(imgset.last_index == 0)
	imgset = imgset["enter"]
	assert(isinstance(imgset, ImageSet))
	assert(imgset.count == 3)
	assert(imgset.last_index == 2)
	assert(os.path.isfile(imgset.images[0]))
	assert(os.path.isfile(imgset.images[0]))
	assert(os.path.isfile(imgset.images[2]))
	imgset = rm.image_set("Block")
	imgset = imgset["b"]["enter"]
	assert(isinstance(imgset, ImageSet))
	assert(imgset.count == 3)
	assert(os.path.isfile(imgset.images[0]))
	assert(os.path.isfile(imgset.images[0]))
	assert(os.path.isfile(imgset.images[2]))


def test_imgset_variant(rm):
	imgset = rm.image_set("Block")
	imgset = imgset.variant("b/enter")
	assert(isinstance(imgset, ImageSet))
	assert(imgset.count == 3)
	assert(os.path.isfile(imgset.images[0]))
	assert(os.path.isfile(imgset.images[0]))
	assert(os.path.isfile(imgset.images[2]))


def test_imgset_from_subpath(rm):
	imgset = rm.image_set("Block/b/enter")
	assert(isinstance(imgset, ImageSet))
	assert(imgset.count == 3)
	assert(os.path.isfile(imgset.images[0]))
	assert(os.path.isfile(imgset.images[0]))
	assert(os.path.isfile(imgset.images[2]))



