import pytest, os
import legame
from legame.game import Game
from legame.resources import *
from pygame import Surface


@pytest.fixture(autouse=True)
def resdump():
	"""
	Returns Resources with "resource_dump" True
	"""
	return FakeGame().dump_resources


@pytest.fixture(autouse=True)
def res():
	"""
	Returns Resources with "resource_dump" False
	"""
	return FakeGame().resources


class FakeGame:
	def __init__(self):
		pygame.mixer.init()
		Game.current = self
		examples = os.path.join(os.path.dirname(legame.__file__), "examples")
		if not os.path.isdir(examples):
			raise NotADirectoryError(examples)
		self.resource_dir = os.path.join(os.path.abspath(examples), "resources")
		if not os.path.isdir(self.resource_dir):
			raise NotADirectoryError(self.resource_dir)
		self.dump_resources = Resources(self.resource_dir, True)
		self.resources = Resources(self.resource_dir, False)


def test_img_path(resdump):
	assert os.path.isfile(resdump.image("Block/r/00.png"))


def test_img_load(res):
	img = res.image("Block/r/00.png", convert = False)
	assert isinstance(img, Surface)


def test_sound_path(resdump):
	assert os.path.isfile(resdump.sound("bust.wav"))


def test_sound_load(res):
	assert isinstance(res.sound("bust.wav"), pygame.mixer.Sound)


def test_svg_load(res):
	img = res.image("test.svg", convert = False)
	assert isinstance(img, Surface)


def test_image_set(resdump):
	imgset = resdump.image_set("Block")
	assert(isinstance(imgset, ImageSet))
	assert(imgset.count == 0)


def test_subset(resdump):
	imgset = resdump.image_set("Block")
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
	imgset = resdump.image_set("Block")
	imgset = imgset.variant("b/enter")
	assert(isinstance(imgset, ImageSet))
	assert(imgset.count == 3)
	assert(os.path.isfile(imgset.images[0]))
	assert(os.path.isfile(imgset.images[0]))
	assert(os.path.isfile(imgset.images[2]))


def test_imgset_variant(resdump):
	imgset = resdump.image_set("Block")
	imgset = imgset.variant("b/enter")
	assert(isinstance(imgset, ImageSet))
	assert(imgset.count == 3)
	assert(os.path.isfile(imgset.images[0]))
	assert(os.path.isfile(imgset.images[0]))
	assert(os.path.isfile(imgset.images[2]))


def test_imgset_from_subpath(resdump):
	imgset = resdump.image_set("Block/b/enter")
	assert(isinstance(imgset, ImageSet))
	assert(imgset.count == 3)
	assert(os.path.isfile(imgset.images[0]))
	assert(os.path.isfile(imgset.images[0]))
	assert(os.path.isfile(imgset.images[2]))


