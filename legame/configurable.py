#  legame/configurable.py
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
import pickle
from os import mkdir
from os.path import dirname, isdir, isfile, join
from appdirs import user_config_dir


class Configurable:

	config_file			= ""
	config				= {}

	def load_config(self):
		config_dir = user_config_dir(self.__class__.__name__)
		self.config_file = join(config_dir, "settings.dat")
		if isfile(self.config_file):
			with open(self.config_file, "rb") as fh:
				self.config = pickle.load(fh)

	def save_config(self):
		if self.config:
			config_dir = dirname(self.config_file)
			if not isdir(config_dir):
				mkdir(config_dir)
			with open(self.config_file, "wb") as fh:
				pickle.dump(self.config, fh)


#  end legame/configurable.py
