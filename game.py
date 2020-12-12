"""Provides the Game class, a framework for games"""

import sys, os, pygame, logging
from pygame.locals import *
from pygame.sprite import Sprite, Rect
from legame.resource_manager import ResourceManager



class Game:
	"""
	This is the base class of games created with the legame library.

	Game.current is a class variable which will contain a reference to the instance
	of the game currently running, and can be used as a "global" variable thoughout
	the code.
	"""

	current				= None		# Not-too-clever substitute for a global variable

	# Game options:
	quiet				= False		# Inhibit sound; mixer is not initialized
	fullscreen			= False
	resource_dump		= False		# Special debugging mode used by ResourceManager; loads filenames instead of files

	# resource manager settings:
	resource_dir		= None		# Directory where game data is located, should contain subfolders "images" and "sounds"
									# Call "set_resource_dir_from_file(__file__)" from your game before Game.__init__
	# display settings:
	display_flags		= 0
	display_depth		= 32
	fps 				= 60
	window_caption		= ""

	# sound settings:
	mixer_frequency		= 22050
	mixer_bitsize		= -16
	mixer_channels		= 8
	mixer_buffer		= 512

	# game objects:
	screen_rect			= None
	background			= None
	screen				= None
	sprites				= None
	resources			= None

	# internal state management:
	_state				= None		# It's pretty important to keep this managed, hence, it's "protected"
	_stay_in_loop		= True		# Setting this to "False" exits the game, calling "exit_loop()"


	LAYER_BG			= 1			#
	LAYER_ABOVE_BG		= 2			#
	LAYER_BELOW_PLAYER	= 4			# Sprite layers
	LAYER_PLAYER		= 6			#
	LAYER_ABOVE_PLAYER	= 8			#
	LAYER_OVERLAY		= 10		#


	def __init__(self, options=None):
		"""

		Game class constructor. Starts the necessary pygame modules, creates the
		ResourceManager and the "sprites" group. You should call this function to
		initialize your game.

		The ResourceManager uses the "resource_dir", an attribute of this class, to
		locate the directory in which images and sounds can be found. Since this
		directory is usually in a path relative to the path to your game, you should
		set this attribute before calling this __init__ function. The helper function
		"set_resource_dir_from_file" sets it for you quite easily.

		The "options" argument is expected to be a dictionary, the items of which are
		set as attributes of the game during initialization. A typical use case would
		be if you used the "optparse" library to read command-line options, and wish to
		pass those options to the Game class before starting up modules. i.e.:

			import sys, optparse
			p = optparse.OptionParser()
			p.add_option('--quiet', '-q', action='store_true')
			p.add_option('--fullscreen', '-f', action='store_true')
			options, arguments = p.parse_args()
			sys.exit(MyGameClass(options.__dict__).run())

		"""
		Game.current = self
		if options is not None:
			for varname, value in options.items():
				setattr(self, varname, value)
		if self.resource_dir is None: self.resource_dir = "resources"
			#raise Exception("No resource_dir defined")
		self.resources = ResourceManager(self.resource_dir, self.resource_dump)
		pygame.display.init()
		pygame.font.init()
		if not self.quiet:
			pygame.mixer.pre_init(self.mixer_frequency, self.mixer_bitsize, self.mixer_channels, self.mixer_buffer)
			pygame.mixer.init()
		self.sprites = pygame.sprite.LayeredUpdates()
		self._event_handlers = {
			ACTIVEEVENT:		self._activeevent,		# 1
			KEYDOWN:			self._keydown,			# 2
			KEYUP:				self._keyup,			# 3
			MOUSEMOTION:		self._mousemotion,		# 4
			MOUSEBUTTONDOWN:	self._mousebuttondown,	# 5
			MOUSEBUTTONUP:		self._mousebuttonup,	# 6
			JOYAXISMOTION:		self._joyaxismotion,	# 7
			JOYBALLMOTION:		self._joyballmotion,	# 8
			JOYHATMOTION:		self._joyhatmotion,		# 9
			JOYBUTTONDOWN:		self._joybuttondown,	# 10
			JOYBUTTONUP:		self._joybuttonup,		# 11
			QUIT:				self._quit,				# 12
			VIDEORESIZE:		self._videoresize,		# 16
			VIDEOEXPOSE:		self._videoexpose,		# 17
		}
		# Fill-in the remaining timer events:
		for event_type in range(USEREVENT, NUMEVENTS+1):
			self._event_handlers[event_type] = self._timer_event
		self.__timer_callbacks = [None for x in range(8)]
		self.__timer_arguments = [None for x in range(8)]
		self.__timer_recur_flag = [None for x in range(8)]


	def set_resource_dir_from_file(self, filename):
		"""
		Set the resource directory to a subfolder of the given file's parent folder.
		If your main game file is located at:
			"/home/user/some/path/game.py"
		... this function will return:
			"/home/user/some/path/resources"
		"""
		self.resource_dir = os.path.join(os.path.dirname(os.path.realpath(filename)), "resources")


	def run(self):
		"""
		Run the game. The "initial_state" function is called from here, and must return an object of class GameState.
		"""
		self.show()
		self._state = self.initial_state()
		self._state.enter_state()
		self._main_loop()
		return 0


	def show(self):
		"""
		Initilizes the screen and shows the initial background. Does not start the game state or begin the _main_loop.
		It is safe to call this function separately, multiple times, and to allow it to be started by Game.run().
		"""
		display_size = (pygame.display.Info().current_w, pygame.display.Info().current_h)
		self.background = self.initial_background(display_size)
		if self.screen is None:
			if self.fullscreen:
				self.screen_rect = Rect((0, 0), display_size)
				self.display_flags |= DOUBLEBUF | FULLSCREEN
			else:
				self.screen_rect = self.background.get_rect()
				self.display_flags |= DOUBLEBUF
				os.environ['SDL_VIDEO_CENTERED'] = '1'
			self.screen = pygame.display.set_mode(
				self.screen_rect.size,
				self.display_flags,
				pygame.display.mode_ok(self.screen_rect.size, self.display_flags, self.display_depth)
			)
		self.screen.blit(self.background, (0,0))
		pygame.display.set_caption(self.window_caption)
		pygame.display.flip()


	def shutdown(self):
		"""
		Triggers the _main_loop to exit. The _main_loop will finish its current iteration before doing so.
		"""
		self._stay_in_loop = False


	##### MAIN LOOP #####

	def _main_loop(self):
		self.clock = pygame.time.Clock()
		self._next_state = None
		while self._stay_in_loop:
			self._state.loop_start()
			for event in pygame.event.get(): self._event_handlers[event.type](event)
			self._end_loop()
			self.sprites.update()
			self.sprites.clear(self.screen, self.background)
			pygame.display.update(self.sprites.draw(self.screen))
			if self._next_state:
				self._state.exit_state(self._next_state);
				self._state = self._next_state
				self._next_state = None		# Note: we must clear next state before entering the new state, in
				self._state.enter_state()	# case the "enter_state" function of the new state sets "_next_state"
			self.clock.tick(self.fps)
		for cls in self.__class__.mro():
			if "exit_loop" in cls.__dict__:
				cls.exit_loop(self)


	def _end_loop(self):
		"""
		Called at the end of the _main_loop().
		The default implementation is to call "loop_end()" on the current GameState.
		This behaviour is overridden in NetworkGame in order to handle message transfer.
		"""
		self._state.loop_end()


	def exit_loop(self):
		"""
		Called when _main_loop() exits, after the final round of moving sprites and updating the display.
		"""
		pass


	# Event handlers:

	def _activeevent(self, event):
		self._state.activeevent(event)

	def _keydown(self, event):
		self._state.keydown(event)

	def _keyup(self, event):
		self._state.keyup(event)

	def _mousemotion(self, event):
		self._state.mousemotion(event)

	def _mousebuttondown(self, event):
		self._state.mousebuttondown(event)

	def _mousebuttonup(self, event):
		self._state.mousebuttonup(event)

	def _joyaxismotion(self, event):
		self._state.joyaxismotion(event)

	def _joyballmotion(self, event):
		self._state.joyballmotion(event)

	def _joyhatmotion(self, event):
		self._state.joyhatmotion(event)

	def _joybuttondown(self, event):
		self._state.joybuttondown(event)

	def _joybuttonup(self, event):
		self._state.joybuttonup(event)

	def _quit(self, event):
		self._state.quit(event)

	def _videoresize(self, event):
		self._state.videoresize(event)

	def _videoexpose(self, event):
		self._state.videoexpose(event)


	# Timers:

	def set_timeout(self, callback, milliseconds, **kwargs):
		"""
		Starts a timer using pygame.time.set_timer() which executes a given callback
		only once.

		The given "callback" is a function to execute after the "milliseconds"
		interval expires. Any keyword arguments after the "milliseconds"
		argument are passed as a dictionary to the given callback function.

		Returns an (integer) index identifying the timer, which can be used to cancel
		the timer by calling "clear_timeout()"
		"""
		return self.__set_timeout(callback, milliseconds, kwargs, False)


	def set_interval(self, callback, milliseconds, **kwargs):
		"""
		Starts a timer using pygame.time.set_timer() which executes a given callback
		at a repeated interval.

		The given "callback" is a function to execute after the "milliseconds"
		interval expires. Any keyword arguments after the "milliseconds"
		argument are passed as a dictionary to the given callback function.

		Returns an (integer) index identifying the timer, which can be used to cancel
		the timer by calling "clear_timeout()"
		"""
		return self.__set_timeout(callback, milliseconds, kwargs, True)


	def clear_timeout(self, timer_index):
		"""
		Clears a timer previously set using "set_timeout()"
		"""
		# logging.debug("Clearing timer %d for timer_index %d" % (USEREVENT + timer_index, timer_index))
		pygame.time.set_timer(USEREVENT + timer_index, 0)
		self.__timer_callbacks[timer_index] = None


	def __set_timeout(self, callback, milliseconds, arguments, recur):
		for timer_index in range(8):
			if self.__timer_callbacks[timer_index] is None:
				self.__timer_callbacks[timer_index] = callback
				self.__timer_arguments[timer_index] = arguments
				self.__timer_recur_flag[timer_index] = recur
				logging.debug("Timer %d calling %s in %d millis" % (timer_index, callback.__name__, milliseconds))
				pygame.time.set_timer(USEREVENT + timer_index, milliseconds)
				return timer_index
		raise Exception("Too many timers!")


	def _timer_event(self, event):
		"""
		Called from the pygame event pump when a timer times out. Executes a timer event.
		You should not call or override this function.
		"""
		timer_index = event.type - USEREVENT	# Subtract USEREVENT constant since our indexes start with 0
		if timer_index > 7:
			raise IndexError("Timer event out of range: " + event_type)
		if self.__timer_callbacks[timer_index] is not None:
			self.__timer_callbacks[timer_index](self.__timer_arguments[timer_index])
			if not self.__timer_recur_flag[timer_index]:
				self.clear_timeout(timer_index)


	def play(self, sound_name):
		"""
		Play a sound identified by "sound_name". If Game.quiet is True, does nothing.
		"""
		if not self.quiet: self.resources.sound(sound_name).play()



class GameState:


	def __init__(self, **kwargs):
		"""
		Set up this GameState to be the new game state next time through the main loop.
		The new state will have attributes set by keyword args passed to this function.
		If the current game state is an instance of "GameStateFinal", the current game
		state will not be changed.
		"""
		for varname, value in kwargs.items(): setattr(self, varname, value)
		if isinstance(Game.current._state, GameStateFinal):
			logging.warn("Changing game state when current state is GameStateFinal is not allowed")
		else:
			Game.current._next_state = self


	def enter_state(self):
		"""
		Function called when the Game transitions TO this state.
		Any information needed to be passed to this GameState should be passed as keyword args to the constructor.
		"""
		pass


	def exit_state(self, next_state):
		"""
		Function called when the Game transitions OUT OF this state.
		The "next_state" parameter is the GameState object which will replace this one.
		"""
		pass


	# Early / late Game._main_loop() events:

	def loop_start(self):
		"""
		Called at the beginning of _main_loop() each time through, before processing events.
		The event loop looks like this:
		1. loop_start()                              <-- you are here
		2. event handling (keyboard, mouse, timers)
		3. loop_end()
		4. move the sprites
		5. update the display
		6. change to new game state (if needed)
		"""
		pass


	def loop_end(self):
		"""
		Called at the end of _main_loop() each time through.
		The event loop looks like this:
		1. loop_start()
		2. event handling (keyboard, mouse, timers)
		3. loop_end()                                <-- you are here
		4. move the sprites
		5. update the display
		6. change to new game state (if needed)
		"""
		pass


	# Event handlers called from Game._main_loop():

	def activeevent(self, event):
		"""
		event will contain: gain, state
		"""
		pass


	def keydown(self, event):
		"""
		Key down event passed to this GameState.
		event will contain: key, mod, unicode, scancode
		"""
		pass


	def keyup(self, event):
		"""
		Key up event passed to this GameState.
		event will contain: key, mod
		"""
		pass


	def mousemotion(self, event):
		"""
		Mouse move event passed to this GameState.
		event will contain:	pos, rel, buttons
		"""
		pass


	def mousebuttondown(self, event):
		"""
		Mouse down event passed to this GameState.
		event will contain:	pos, button
		"""
		pass


	def mousebuttonup(self, event):
		"""
		Mouse up event passed to this GameState.
		event will contain: pos, button
		"""
		pass


	def joyaxismotion(self, event):
		"""
		Joystick motion event passed to this GameState.
		event will contain:	instance_id, axis, value
		"""
		pass


	def joyballmotion(self, event):
		"""
		Joystick ball motion event passed to this GameState.
		event will contain:	instance_id, ball, rel
		"""
		pass


	def joyhatmotion(self, event):
		"""
		Joystick hat motion event passed to this GameState.
		event will contain: instance_id, hat, value
		"""
		pass


	def joybuttondown(self, event):
		"""
		Joystick button down event passed to this GameState.
		event will contain: instance_id, button
		"""
		pass


	def joybuttonup(self, event):
		"""
		Joystick button up event passed to this GameState.
		event will contain:	instance_id, button
		"""
		pass


	def quit(self, event):
		"""
		Event handler called when the user clicks the window's close button.
		event will be empty
		"""
		Game.current.shutdown()


	def videoresize(self, event):
		"""
		Event handler called when the window / display is resized.
		event will contain: size, w, h
		"""
		pass


	def videoexpose(self, event):
		"""
		Event handler called when the window is exposed(?)
		event will be empty
		"""
		pass



class GameStateFinal(GameState):
	"""
	Final GameState - cannot be replaced even if a new GameState is instantiated after this one.
	See exit_states.py for an example.
	"""
	pass



