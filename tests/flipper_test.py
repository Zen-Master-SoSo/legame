#  legame/tests/flipper_test.py
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
		self.resources = Resources(self.resource_dir, True)


class Block(Flipper):
	image_folder	= "Block/r"
	def __init__(self):
		Flipper.__init__(self, FlipThrough("enter"))


def test_flip_through_once(thing):
	assert isinstance(thing.flipper, FlipThrough)
	assert thing.flipper.loop_forever == False
	assert thing.flipper.loops == 1
	assert thing.image == thing.flipper.image_set.images[0]
	for frame in [0, 1, 2]:
		assert thing.flipper.frame == frame
		thing.update()
	assert thing.flipper is None


def test_flip_through_twice(thing):
	thing.flip(FlipThrough("enter", loops=2))
	assert thing.flipper.loop_forever == False
	assert(thing.flipper.loops == 2)
	for frame in [0, 1, 2, 0, 1, 2]:
		assert thing.flipper.frame == frame
		thing.update()
	assert thing.flipper is None


def test_between_through_once(thing):
	thing.flip(FlipBetween("jiggle"))
	assert isinstance(thing.flipper, FlipBetween)
	assert thing.flipper.loop_forever == False
	assert thing.flipper.loops == 1
	for frame in [0, 1, 2, 1, 0]:
		assert thing.flipper.frame == frame
		thing.update()
	assert thing.flipper is None


def test_flip_between_twice(thing):
	thing.flip(FlipBetween("jiggle", loops=2))
	assert thing.flipper.loop_forever == False
	assert(thing.flipper.loops == 2)
	assert(thing.image == thing.flipper.image_set.images[0])
	for frame in [0, 1, 2, 1, 0, 1, 2, 1, 0]:
		assert thing.flipper.frame == frame
		thing.update()
	assert thing.flipper is None


def test_flip_through_loop_forever(thing):
	thing.flip(FlipThrough("enter", loop_forever=True))
	assert thing.flipper.loop_forever == True
	assert thing.flipper.frame == 0
	for frame in [0, 1, 2, 0, 1, 2, 0, 1, 2, 0, 1, 2, 0, 1, 2]:
		assert thing.flipper.frame == frame
		thing.update()


def test_two_flippers_queued(thing):
	thing.flip(FlipBetween("jiggle"), FlipThrough("enter"))
	assert(thing.flipper.__class__.__name__ == "FlipBetween")
	assert thing.flipper.loop_forever == False
	assert thing.flipper.loops == 1
	assert thing.flipper.frame == 0
	for frame in [0, 1, 2, 1, 0]:
		assert thing.flipper.frame == frame
		thing.update()
	assert(thing.flipper.__class__.__name__ == "FlipThrough")
	assert thing.flipper.loop_forever == False
	assert thing.flipper.loops == 1
	assert thing.flipper.frame == 0
	for frame in [0, 1, 2]:
		assert thing.flipper.frame == frame
		thing.update()
	assert thing.flipper is None


def test_starting_frame(thing):
	thing.flip(FlipBetween("jiggle", loop_forever=True, frame=2, fps=30))
	assert thing.flipper.loop_forever == True
	assert thing.flipper.frame == 2


#  end legame/tests/flipper_test.py
