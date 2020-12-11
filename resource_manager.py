"""
Provides the ResourceManager class which loads images and sounds on demand,
allowing access to these based on keywords and indexes.
"""

import os, re, pygame


class ResourceManager:

	def __init__(self, path=None, resource_dump=False):
		self.image_folder = os.path.join(path, "images")
		self.sounds_folder = os.path.join(path, "sounds")
		self.resource_dump = resource_dump
		self.sounds = {}
		self.images = {}
		self.image_sets = {}
		self.dirty= False


	def sound(self, name):
		if name not in self.sounds:
			path = os.path.join(self.sounds_folder, name)
			if self.resource_dump:
				self.sounds[name] = path
			else:
				self.sounds[name] = pygame.mixer.Sound(path)
			self.dirty = True
		return self.sounds[name]


	def image(self, name, alpha_channel=True, color_key=None):
		"""
		Returns a pygame Surface with the given image loaded and converted to the screen format.
		You may provide a name which includes subpaths, i.e.:

			white_rook.image = <resource_manager>.image("ChessPiece/White/rook.png")

		The actual filesystem path will be relative to the ResourceManager "image_folder".

		"""
		if name not in self.images:
			path = os.path.join(self.image_folder, name)
			if self.resource_dump:
				self.images[name] = path
			else:
				self.images[name] = pygame.image.load(path)
				if alpha_channel and color_key is None:
					self.images[name].convert_alpha()
				else:
					self.images[name].convert()
					if color_key is not None: self.images[name].set_colorkey(color_key)
			self.dirty = True
		return self.images[name]


	def image_set(self, path, alpha_channel=True, color_key=None):
		"""
		Returns an ImageSet, which provides a list of images and variants.
		(See ResourceManager.ImageSet)
		"""
		if "/" in path:
			parts = path.split("/")
			name = parts[0]
			variants = parts[1:]
		else:
			name = path
			variants = []
		if name not in self.image_sets:
			self.image_sets[name] = ImageSet(self.image_folder, name, \
				alpha_channel=alpha_channel, color_key=color_key, resource_dump=self.resource_dump)
			self.dirty = True
		imgset = self.image_sets[name]
		for variant in variants:
			imgset = imgset.variants[variant]
		return imgset


	def preload_sounds(self):
		"""
		Loads all sound files found in ResourceManager "sounds_folder".
		"""
		for filename in os.listdir(self.sounds_folder):
			self.sounds[filename] = pygame.mixer.Sound(os.path.join(self.sounds_folder, filename))


	def dump(self):
		"""
		Diagnostic function which dumps the filenames of the loaded resources to STDOUT.
		You must intialize the ResourceManager using the "resource_dump" flag for the
		resources to load as path names rather than actual Image and Sound instances.
		"""
		if len(self.sounds):
			print("Sounds")
			print("-" * 40)
			for title in self.sounds: print("  %s" % title)
			print("")
		if len(self.images):
			print("Images")
			print("-" * 40)
			for title in self.images: print("  %s" % title)
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

	image_extensions	= [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tga"]


	def __init__(self, images_dir, name, alpha_channel=True, color_key=None, resource_dump=False):
		"""
		Creates an ImageSet by loading the images found in specified directory.
		"images_dir" is the directory that ResourceManager uses as the base directory
		for images. This is commonly "<game directory>/resources/images", when using
		standard directory naming conventions.
		"name" will be the name that the ImagesSet is referred to as, and is also the
		name of the directory below "images_dir" where the image files may be found.

		ImageSets are used by the "Flipper" and "ImageCycle" classes to provide the
		images used by these classes to animate sprites. However, you can use an
		ImageSet outside of these classes as well.

		An ImageSet contains a list of "images", which are pygame Surface objects
		created from loading image files. Additionally, the ImageSet has a list of
		"variants", which are themselves ImageSet instances, which may contain images
		and variants.

		The "variants" correlate to subfolders below the "images_dir/name" folder. When
		the top-level ImageSet is loaded, all the variants are loaded as well.

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

			white_pieces = ImageSet(<resource_manager>.image_folder, "ChessPiece/White")

		...or...

			white_pieces = <resource_manager>.image_set("ChessPiece/White")

		Note, however, that the individual IMAGES in the ImageSet instantiated above
		would still have numeric indexes, since the "images" attribute is a list, and
		not a dict. So you may not reference the individual white chess pieces by name,
		but will have to refer to them by their index, like so:

			white_rook.image = white_pieces.images[5]

		We can be sure that "rook" is the last item in the list (6 pieces, indexes
		starting at 0), because the ImageSet always sorts the names of the image files
		after they have been read, and compiles the list in a natural sort order. This
		is necessary for performative function of the "Flipper" and "ImageCycle"
		classes, the trade-off being that you simply have to deal with numeric indexes
		if you wish to directly reference images in an ImageSet.

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
		ResourceManager.image() to load each image individually. In that case, the
		ChessPiece images might be referenced using the following syntax:

			white_rook.image = <resource_manager>.image("ChessPiece/White/rook.png")

		"""
		self.variants = {}
		self.name = name
		self.resource_dump = resource_dump
		my_root = os.path.join(images_dir, name)
		if not os.path.isdir(my_root):
			raise NotADirectoryError(my_root)
		images = {}
		for entry in os.scandir(my_root):
			if entry.is_dir(follow_symlinks=True):
				self.variants[entry.name] = ImageSet(my_root, entry.name, \
					alpha_channel=alpha_channel, color_key=color_key, resource_dump=resource_dump)
			elif entry.is_file(follow_symlinks=True):
				filetitle, ext = os.path.splitext(entry.name)
				if ext in self.image_extensions:
					# append image to temporary dictionary, unsorted:
					if self.resource_dump:
						images[entry.name] = entry.path
					else:
						images[entry.name] = pygame.image.load(entry.path)
						if alpha_channel and color_key is None:
							images[entry.name].convert_alpha()
						else:
							images[entry.name].convert()
							if color_key is not None: images[entry.name].set_colorkey(color_key)
		self.count = len(images)
		self.last_index = self.count - 1
		if self.count:
			# Create list of images from sorted keys, using "human" number sorting ("10" comes after "2")
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


	def __getitem__(self, key):
		return self.variants[key] if key in self.variants else self.images[key]


	def dump(self):
		self.__dump(self.name, 0)


	def __dump(self, keyname, indent):
		print(("   " * indent + "%s: %d images") % (keyname, self.count))
		for key, imgset in self.variants.items():
			imgset.__dump(key, indent + 1)



