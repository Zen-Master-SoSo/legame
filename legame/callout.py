""" Provides the Callout class, a Sprite used during development to provide debug
information positioned near another animated sprite. """

from pygame import Rect, Surface
from pygame.sprite import Sprite


class Callout(Sprite):

	def __init__(self, sprite, group, font):
		Sprite.__init__(self, group)
		self.sprite = sprite
		self.rect = Rect((sprite.rect.right, sprite.rect.bottom, 0, 0))
		self.image = Surface((0, 0))
		self.font = font
		self.empty()

	def empty(self):
		self.texts = []
		self.rect.width = 0

	def write(self, text, color=(255, 255, 255)):
		self.texts.append(self.font.render(text, True, color))
		width, height = self.font.size(text)
		if width > self.rect.width:
			self.rect.width = width
		self.rect.height += height

	def update(self):
		self.rect.left = self.sprite.rect.right
		self.rect.top = self.sprite.rect.bottom
		self.image = Surface((self.rect.width, self.rect.height))
		self.image.set_colorkey((0,0,0))
		self.image.fill((0,0,0))
		line_height = self.font.get_linesize()
		y = 0
		for s in self.texts:
			self.image.blit(s, (0, y))
			y += line_height
		self.rect.height = y

