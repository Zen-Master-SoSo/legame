import pygame
from pygame.locals import SRCALPHA
from cairosvg.parser import Tree
from cairosvg.surface import PNGSurface
from cairosvg.surface.helpers import node_format
try:
	import lxml.etree as ET
except ImportError:
	import xml.etree as ET


class svg:

	@classmethod
	def load(cls, filename, **kwargs):
		with open(filename, "rb") as fh: return cls.from_xml(fh.read(), **kwargs)


	@classmethod
	def from_xml(cls, xml, **kwargs):
		cairosvg_tree = Tree(bytestring=xml)
		width, height, viewbox = node_format(None, cairosvg_tree)
		return cls.__surf_from_cairosvgtree(cairosvg_tree, width, height, **kwargs)


	@classmethod
	def svg_rotated(cls, xml, step, center_x=None, center_y=None, **kwargs):
		images = []
		svg_node = ET.fromstring(xml)
		wrapper = ET.SubElement(svg_node, "g", { "id": "legame-image-rotator", "transform": "" })
		for e in svg_node:
			if e is not wrapper:
				wrapper.append(e)
		# Create cairosvg.Tree
		# use the cairosvg.surface.helpers.node_format() func to get width, height:
		cairosvg_tree = Tree(bytestring = ET.tostring(svg_node.getroottree()))
		width, height, viewbox = node_format(None, cairosvg_tree)
		if center_x is None: center_x = width / 2
		if center_y is None: center_y = height / 2
		for degrees in range(0, 360, step):
			cairosvg_tree.children[0]["transform"] = "rotate({}, {}, {})".format(degrees, center_x, center_y)
			images.append(cls.__surf_from_cairosvgtree(cairosvg_tree, width, height, **kwargs))
		return images

	@classmethod
	def __surf_from_cairosvgtree(cls, cairosvg_tree, width, height, **kwargs):
		"""
		Takes a cairosvg.Tree, and its interpreted width, height
		Returns a pygame.Surface
		"""
		csurf = PNGSurface(cairosvg_tree, bytes, 92.0)
		surf = pygame.Surface((csurf.cairo.get_width(), csurf.cairo.get_height()), SRCALPHA, 32)
		surf.get_buffer().write(csurf.cairo.get_data())
		surf.unlock()
		return surf





if __name__ == "__main__":
	import sys, os


	with open("tests/test.svg", "rb") as fh: xml = fh.read()
	images = svg.svg_rotated(xml, 30)

	pygame.init()
	os.environ['SDL_VIDEO_CENTERED'] = '1'
	rect = images[0].get_rect()
	window = pygame.display.set_mode(rect.inflate(80, 80).size)
	center = window.get_rect().move(-rect.width / 2, -rect.height / 2).center
	screen = pygame.display.get_surface()
	screen.fill((180,180,180))

	i = 0
	clock = pygame.time.Clock()
	while True:
		clock.tick(30)
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				raise SystemExit
			elif event.type == pygame.KEYDOWN and (event.key == pygame.K_ESCAPE or event.key == pygame.K_q):
				raise SystemExit
		screen.fill((180,180,180))

		screen.blit(images[i], center)
		i -= 1
		if i < 0: i = len(images) - 1

		pygame.display.flip()


