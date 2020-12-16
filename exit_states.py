"""
Provides GameState classes which exit a game after showing an animated message.
"""
from pygame.time import wait
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
		if self.rect.centery < Game.current.background.get_rect().centery:
			self.rect.centery = min(self.rect.centery + self.__frame_step, Game.current.background.get_rect().centery)
		else:
			wait(self.game_over_delay)
			Game.current.shutdown()



