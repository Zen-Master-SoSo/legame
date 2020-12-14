import pytest, os
import legame
from legame.game import Game
from legame.resources import *


@pytest.fixture(autouse=True)
def res():
	return FakeGame().resources


class FakeGame:
	def __init__(self):
		Game.current = self
		examples = os.path.join(os.path.dirname(legame.__file__), "examples")
		if not os.path.isdir(examples):
			raise NotADirectoryError(examples)
		self.resource_dir = os.path.join(os.path.abspath(examples), "resources")
		if not os.path.isdir(self.resource_dir):
			raise NotADirectoryError(self.resource_dir)
		self.resources = Resources(self.resource_dir, True)


def test_sound_loader(res):
	assert os.path.isfile(res.sound("bust.wav"))


def test_image_set(res):
	imgset = res.image_set("Block")
	assert(isinstance(imgset, ImageSet))
	assert(imgset.count == 0)


def test_subset(res):
	imgset = res.image_set("Block")
	imgset = imgset.variant("b")
	assert(isinstance(imgset, ImageSet))
	assert(imgset.count == 1)
	assert(imgset.last_index == 0)
	imgset = imgset.variant("enter")
	assert(isinstance(imgset, ImageSet))
	assert(imgset.count == 3)
	assert(imgset.last_index == 2)
	assert(os.path.isfile(imgset.images[0]))
	assert(os.path.isfile(imgset.images[0]))
	assert(os.path.isfile(imgset.images[2]))
	imgset = res.image_set("Block")
	imgset = imgset.variant("b/enter")
	assert(isinstance(imgset, ImageSet))
	assert(imgset.count == 3)
	assert(os.path.isfile(imgset.images[0]))
	assert(os.path.isfile(imgset.images[0]))
	assert(os.path.isfile(imgset.images[2]))


def test_imgset_variant(res):
	imgset = res.image_set("Block")
	imgset = imgset.variant("b/enter")
	assert(isinstance(imgset, ImageSet))
	assert(imgset.count == 3)
	assert(os.path.isfile(imgset.images[0]))
	assert(os.path.isfile(imgset.images[0]))
	assert(os.path.isfile(imgset.images[2]))


def test_imgset_from_subpath(res):
	imgset = res.image_set("Block/b/enter")
	assert(isinstance(imgset, ImageSet))
	assert(imgset.count == 3)
	assert(os.path.isfile(imgset.images[0]))
	assert(os.path.isfile(imgset.images[0]))
	assert(os.path.isfile(imgset.images[2]))



