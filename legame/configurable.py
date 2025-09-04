import pickle
from appdirs import user_config_dir


class Configurable:

	config_file			= ""
	config				= {}


	def load_config(self):
		config_dir = user_config_dir(self.__class__.__name__)
		self.config_file = os.path.join(config_dir, "settings.dat")
		if os.path.isfile(self.config_file):
			with open(self.config_file, "rb") as fh:
				self.config = pickle.load(fh)


	def save_config(self):
		if self.config:
			config_dir = os.path.dirname(self.config_file)
			if not os.path.isdir(config_dir):
				os.mkdir(config_dir)
			with open(self.config_file, "wb") as fh:
				pickle.dump(self.config, fh)

