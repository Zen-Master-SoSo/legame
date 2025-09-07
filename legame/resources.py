#  legame/resources.py
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
Provides the Resources class which loads images and sounds on demand, allowing
access to these based on keywords and indexes.
"""
import os, re
from pygame.image import load as image_load
from pygame.mixer import Sound


class Resources:

	def __init__(self, path = None, resource_dump = False):
		self.image_folder = os.path.join(path, "images")
		self.sounds_folder = os.path.join(path, "sounds")
		self.resource_dump = resource_dump
		self.sounds = {}
		self.images = {}
		self.image_sets = {}

	def sound(self, name):
		"""
		Return a "Sound" object from the file found at the given name.
		"""
		if name not in self.sounds:
			path = os.path.join(self.sounds_folder, name)
			if self.resource_dump:
				self.sounds[name] = path
			else:
				self.sounds[name] = Sound(path)
		return self.sounds[name]

	def image(self, name, **kwargs):
		"""
		Returns a pygame Surface with the given image loaded and converted to the
		screen format. You may provide a name which includes subpaths, i.e.:

			white_rook.image = <resources>.image("ChessPiece/White/rook.png")

		The actual filesystem path will be relative to the Resources "image_folder".

		"kwargs" may include: "convert", "convert_alpha", or "color_key". These trigger
		calling the appropriate pygame.Surface function after the image is loaded.

		From the pygame documentation for Surface.convert():

			[T]he new Surface will have the same pixel format as the display Surface. This
			is always the fastest format for blitting. It is a good idea to convert all
			Surfaces before they are blitted many times.

		Note: the "color_key" option overrides both "convert" and "convert_alpha".

		For a full description of alpha channels and color key alphas, see the pygame
		documentation.
		"""
		if name not in self.images:
			path = os.path.join(self.image_folder, name)
			if self.resource_dump:
				self.images[name] = path
			else:
				title, ext = os.path.splitext(name)
				self.images[name] = image_load(path)

				convert = kwargs.get("convert", False)
				convert_alpha = kwargs.get("convert_alpha", False)
				color_key = kwargs.get("color_key", None)

				if (convert or convert_alpha) and color_key is None:
					if convert_alpha:
						self.images[name].convert_alpha()
					else:
						self.images[name].convert()
				elif color_key is not None:
					self.images[name].set_colorkey(color_key)

		return self.images[name]

	def image_set(self, path, **kwargs):
		"""
		Returns an ImageSet, which provides a list of images and variants.
		For an explantation of the "convert_alpha" and "color_key" options, see
		Resource.image()
		"""
		if "/" in path:
			parts = path.split("/")
			name = parts[0]
			variants = parts[1:]
		else:
			name = path
			variants = []
		if name not in self.image_sets:
			self.image_sets[name] = ImageSet(self.image_folder, name,
				resource_dump = self.resource_dump, **kwargs)
		imgset = self.image_sets[name]
		for variant in variants: imgset = imgset.variants[variant]
		return imgset

	def preload_sounds(self):
		"""
		Loads all sound files found in Resources "sounds_folder".
		"""
		for filename in os.listdir(self.sounds_folder):
			self.sounds[filename] = Sound(os.path.join(self.sounds_folder, filename))

	def dump(self):
		"""
		Diagnostic function which dumps the filenames of the loaded resources to STDOUT.
		You must intialize the Resources using the "resource_dump" flag for the
		resources to load as path names rather than actual Image and Sound instances.
		"""
		if len(self.sounds):
			print("Sounds")
			print("-" * 40)
			for title in self.sounds: print(f"  {title}")
			print("")
		if len(self.images):
			print("Images")
			print("-" * 40)
			for title in self.images: print(f"  {title}")
			print("")
		print("Image Sets")
		print("-" * 40)
		for img_set in self.image_sets.values():
			img_set.dump()
		print("-" * 40)
		print("""
Note: Some resources might not be enumurated here.
If you use Flipper.preload(), only classes which subclass Flipper will have
image sets loaded. It may be possible to use an image set which is not cycled
using the Flipper class, in which case those images will have not been loaded.
			""")


class ImageSet:
	"""
	A class which keeps a group (or groups) of Image objects. ImageSets are used by
	the "Flipper" and "FlipEffect" classes to provide the images used by these
	classes to animate sprites. You can also use an ImageSet separately as well.

	An ImageSet contains a list of "images", which are pygame Surface objects
	created from loading image files. Additionally, the ImageSet has a dicitonary
	of "variants", which are themselves instances of ImageSet which contain images
	and variants. The "variants" correlate to subfolders. When the top-level
	ImageSet is loaded, all the variants are loaded as well.

	Images are referenced with the numeric indexes of "ImageSet.images". Variants
	are referenced with string keys of "ImageSet.variants".

	The parent ImageSet may or may not contain images. An image set which only
	contains variants which themselves contain images is perfectly okay. For
	example, you could have a top-level "ChessPiece" ImageSet which contains only
	two variants: "White" and "Black. These ImageSet objects would contain the
	actual images, one with white pieces, and one with black.

	This is best described using an illustration. Using the "ChessPiece" ImageSet
	example above, the folder hierarcy would look like this:

		<project folder>
		|-- <your_game.py>
		|-- resources
			|-- images
				|-- ChessPiece
					|-- Black
					|	|-- bishop.png
					|	|-- king.png
					|	|--	knight.png
					|	|-- pawn.png
					|	|-- queen.png
					|	|-- rook.png
					|-- White
						|-- bishop.png
						|-- king.png
						|--	knight.png
						|-- pawn.png
						|-- queen.png
						|-- rook.png

	When referencing the White pieces ImageSet, you would use the following
	syntax:

		white_pieces = ImageSet(<resources>.image_folder, "ChessPiece/White")

	...or...

		white_pieces = <resources>.image_set("ChessPiece/White")

	Note, however, that the individual images in the ImageSet instantiated above
	would still have numeric indexes, since the "images" attribute is a list, and
	not a dict. So you may not reference the individual white chess pieces by name,
	but will have to refer to them by their index, like so:

		white_rook.image = white_pieces.images[5]

	We can be sure that "rook" is the last item in the list with index "5" (out of
	6 pieces; list indexes always start at 0), because the ImageSet sorts the image
	files by name using a natural sort order. This is necessary for the the
	"Flipper" and "FlipEffect" classes.

	By "natural language sorting" we mean that numbers in the file name are sorted
	in the order that a human would expect. So "2" comes before "10". A simple sort
	of ASCII values doesn't do that:

		ASCII sort:
		-----------
		file10.png
		file15.png
		file1.png
		file20.png
		file25.png
		file2.png

		Nat sort:
		-----------
		file1.png
		file2.png
		file10.png
		file15.png
		file20.png
		file25.png

	If you would like to avoid using numeric indexes, consider using
	Resources.image() to load each image individually. In that case, the
	ChessPiece images might be referenced using the following syntax:

		white_rook.image = <resources>.image("ChessPiece/White/rook.png")

	"""

	image_extensions	= [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tga"]

	def __init__(self, images_dir, name, **kwargs):
		"""
		Creates an ImageSet by loading the images found in specified directory.
		"images_dir" is the directory that Resources uses as the base directory
		for images. This is commonly "<game directory>/resources/images", when using
		standard directory naming conventions.

		"name" will be the name that the ImagesSet is referred to as, and is also the
		name of the directory below "images_dir" where the image files may be found.

		"kwargs" may include: "convert", "convert_alpha", "color_key" or "resource_dump".

		When "resource_dump" is True, images and sounds will not be loaded. Instead,
		path names will be loaded in their place for debugging.

		For an explanation of "convert", "convert_alpha" and "color_key" options, see
		the Resource.image() function.
		"""

		self.variants = {}
		self.images = []
		self.name = name
		self.resource_dump = kwargs.get("resource_dump", False)
		convert = kwargs.get("convert", False)
		convert_alpha = kwargs.get("convert_alpha", True)
		color_key = kwargs.get("color_key", None)
		my_root = os.path.join(images_dir, name)
		if not os.path.isdir(my_root):
			raise NotADirectoryError(my_root)
		images = {}
		for entry in os.scandir(my_root):
			if entry.is_dir(follow_symlinks = True):
				self.variants[entry.name] = ImageSet(my_root, entry.name, **kwargs)
			elif entry.is_file(follow_symlinks = True):
				_, ext = os.path.splitext(entry.name)
				if ext in self.image_extensions:
					# append image to temporary dictionary, unsorted:
					if self.resource_dump:
						images[entry.name] = entry.path
					else:
						images[entry.name] = image_load(entry.path)
						if (convert or convert_alpha) and color_key is None:
							if convert_alpha:
								images[entry.name].convert_alpha()
							else:
								images[entry.name].convert()
						elif color_key is not None:
							images[entry.name].set_colorkey(color_key)
		self.count = len(images)
		self.last_index = self.count - 1
		if self.count:
			# Create list of images using "human" number sorting ("10" comes after "2")
			convert = lambda text: int(text) if text.isdigit() else text
			alphanum_key = lambda key: [ convert(c) for c in re.split('([0-9]+)', key) ]
			self.images = [images[key] for key in sorted(images, key = alphanum_key)]

	def variant(self, path):
		"""
		Returns an ImageSet which is a variant of this ImageSet.
		"""
		imgset = self
		for arg in path.split("/"):
			imgset = imgset.variants[arg]
		return imgset

	def dump(self):
		"""
		Print the path names of the images loaded for debugging.
		"""
		self._dump(self.name, 0)

	def _dump(self, keyname, indent):
		print(("   " * indent + "%s: %d images") % (keyname, self.count))
		for key, imgset in self.variants.items():
			imgset._dump(key, indent + 1)


#  end legame/resources.py
