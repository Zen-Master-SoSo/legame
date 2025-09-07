#  legame/exit_states.py
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
Provides GameState classes which exit a game after showing an animated message.
"""
from pygame.sprite import Sprite
from legame.game import Game, GameStateFinal


class GSExitAnimation(GameStateFinal):
	"""
	A game state which shows an animated message, which shuts down the game when complete.
	"""

	def enter_state(self):
		ExitAnimation(self.image)


class GSWon(GSExitAnimation):

	image = "you-win.png"


class GSLost(GSExitAnimation):

	image = "game-over.png"


class GSQuit(GSExitAnimation):

	image = "bye-bye.png"


class ExitAnimation(Sprite):
	"""
	An animated sprite which drops down from the top of the display, and closes the
	current game when the animation is complete.
	"""

	anim_duration		= 0.33
	game_over_delay		= 777
	exit_timer			= None

	def __init__(self, image):
		Sprite.__init__(self, Game.current.sprites)
		Game.current.sprites.change_layer(self, Game.LAYER_OVERLAY)
		self.image = Game.current.resources.image(image)
		self.rect = self.image.get_rect()
		self.rect.top = -self.rect.height
		self.rect.centerx = Game.current.screen_rect.centerx
		self.__frame_step = (Game.current.screen_rect.centery - self.rect.centery) \
			// self.anim_duration // Game.current.fps

	def update(self):
		if self.exit_timer is None:
			centery = Game.current.background.get_rect().centery
			if self.rect.centery < centery:
				self.rect.centery = min(self.rect.centery + self.__frame_step, centery)
			else:
				self.exit_timer = Game.current.set_timeout(Game.current.shutdown, self.game_over_delay)


#  end legame/exit_states.py
