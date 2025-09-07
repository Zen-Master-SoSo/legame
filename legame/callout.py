#  legame/callout.py
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
Provides the Callout class, a Sprite used during development to provide debug
information positioned near another animated sprite.
"""
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

	def write(self, text, color = (255, 255, 255)):
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


#  end legame/callout.py
