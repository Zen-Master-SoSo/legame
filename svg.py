import pygame
from math import floor
from pygame.locals import SRCALPHA
from cairosvg.parser import Tree
from cairosvg.surface import PNGSurface
from cairosvg.surface.helpers import node_format
try:
	import lxml.etree as ET
except ImportError:
	import xml.etree as ET



def load(filename):
	with open(filename, "rb") as fh:
		return from_xml(fh.read())



def from_xml(xml):
	cairosvg_tree = Tree(bytestring=xml)
	width, height, viewbox = node_format(None, cairosvg_tree)
	return surf_from_cairosvgtree(cairosvg_tree, width, height)



def rotated_svg(filename, **kwargs):
	"""
	Returns a pygame.Surface list from the given file.
	kwargs may include:
		degrees:	Number of degrees to rotate each frame.	\
		frames:		Number of frames to generate			 | these arguments
		images:		Same as "frames"						 | are
		rotations:	List of angles to rotate, in degrees.	 | mutually exclusive
					The returned list will be the same len	/
		center_x, center_y:
					Center of rotation
	"""
	with open(filename, "rb") as fh:
		return svg_xml_rotated(fh.read(), **kwargs)



def svg_xml_rotated(xml, **kwargs):
	"""
	Returns a pygame.Surface list from the given xml.
	For kwargs, see "rotated_svg"
	"""
	degrees = kwargs.pop("degrees", None)
	images = kwargs.pop("images", None)
	frames = kwargs.pop("frames", images)
	rotations = kwargs.pop("rotations", None)
	center_x = kwargs.pop("center_x", None)
	center_y = kwargs.pop("center_y", None)
	if center_x and not center_y or center_y and not center_x:
		raise Exception("Invalid center - must provide both center_x and center_y, or none")
	if len(kwargs): logging.warning("Unexpected keyword arguments: %s" % kwargs)

	if rotations:
		if degrees or frames: raise Exception("Incompatible arguments")
	else:
		if degrees:
			if frames: raise Exception("Incompatible arguments")
			frames = floor(360 / degrees)
		elif frames:
			if degrees: raise Exception("Incompatible arguments")
			degrees = 360 / frames
		else:
			raise Exception("No rotation spec!")
		rotations = [degrees * i for i in range(frames)]

	images = []

	# Read the svg into ElementTree:
	svg_node = ET.fromstring(xml)
	# Create group with transform to contain rest of svg:
	wrapper = ET.SubElement(svg_node, "g", { "id": "legame-image-rotator", "transform": "" })
	# Move all nodes not the wrapper to inside the wrapper:
	for e in svg_node:
		if e is not wrapper:
			wrapper.append(e)
	# Create cairosvg.Tree to be rendered
	# use the cairosvg.surface.helpers.node_format() func to get width, height:
	cairosvg_tree = Tree(bytestring = ET.tostring(svg_node.getroottree()))
	width, height, viewbox = node_format(None, cairosvg_tree)
	if center_x is None: center_x = width / 2
	if center_y is None: center_y = height / 2

	for degrees in rotations:
		# Modify "transform" attribute of wrapper node:
		cairosvg_tree.children[0]["transform"] = "rotate({}, {}, {})".format(degrees, center_x, center_y)
		# Render modified cairosvg Tree:
		images.append(surf_from_cairosvgtree(cairosvg_tree, width, height))
	return images



def surf_from_cairosvgtree(cairosvg_tree, width, height):
	"""
	Takes a cairosvg.Tree, and its interpreted width, height
	Returns a pygame.Surface
	"""
	cairo_surface = PNGSurface(cairosvg_tree, bytes, 92.0)
	pygame_surf = pygame.Surface((cairo_surface.cairo.get_width(), cairo_surface.cairo.get_height()),
		SRCALPHA, int(cairo_surface.cairo.get_stride() / cairo_surface.cairo.get_width() * 8))
	pygame_surf.get_buffer().write(cairo_surface.cairo.get_data())
	pygame_surf.unlock()
	return pygame_surf





if __name__ == "__main__":
	import sys, os

	images = rotated_svg("examples/resources/images/test.svg", degrees=10)

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


