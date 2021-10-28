"""
Provides the Game and GameState classes, a framework for writing games.
"""

import sys, os, pygame, logging
from pygame.locals import DOUBLEBUF, FULLSCREEN, SCALED, USEREVENT, NUMEVENTS, \
	 ACTIVEEVENT, \
	 AUDIODEVICEADDED, AUDIODEVICEREMOVED, \
	 CONTROLLERAXISMOTION, CONTROLLERBUTTONDOWN, CONTROLLERBUTTONUP, \
	 CONTROLLERDEVICEADDED, CONTROLLERDEVICEREMAPPED, CONTROLLERDEVICEREMOVED, \
	 DROPBEGIN, DROPCOMPLETE, DROPFILE, DROPTEXT, \
	 FINGERDOWN, FINGERMOTION, FINGERUP, \
	 JOYAXISMOTION, JOYBALLMOTION, JOYBUTTONDOWN, JOYBUTTONUP, JOYDEVICEADDED, JOYDEVICEREMOVED, JOYHATMOTION, \
	 KEYDOWN, KEYUP, \
	 MIDIIN, MIDIOUT, \
	 MOUSEBUTTONDOWN, MOUSEBUTTONUP, MOUSEMOTION, MOUSEWHEEL, \
	 MULTIGESTURE, QUIT, SYSWMEVENT, \
	 TEXTEDITING, TEXTINPUT, \
	 VIDEOEXPOSE, VIDEORESIZE, \
	 WINDOWCLOSE, WINDOWENTER, WINDOWEXPOSED, WINDOWFOCUSGAINED, WINDOWFOCUSLOST, \
	 WINDOWHIDDEN, WINDOWHITTEST, WINDOWLEAVE, WINDOWMAXIMIZED, WINDOWMINIMIZED, \
	 WINDOWMOVED, WINDOWRESIZED, WINDOWRESTORED, WINDOWSHOWN, WINDOWSIZECHANGED, WINDOWTAKEFOCUS
from legame.resources import Resources



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
	resource_dump		= False		# Special debugging mode used by Resources; loads filenames instead of files

	# resource manager settings:
	resource_dir		= None		# Directory where game data is located, should contain subfolders "images" and "sounds"
									# Call "set_resource_dir_from_file(__file__)" from your game before Game.__init__
	# display settings:
	fps 				= 60
	display_flags		= DOUBLEBUF
	display_depth		= 32
	caption				= ""
	icon				= None

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
	__next_state		= None		# Next game state waiting for change at end of main loop


	LAYER_BG			= 1			#
	LAYER_ABOVE_BG		= 2			#
	LAYER_BELOW_PLAYER	= 4			# Sprite layers
	LAYER_PLAYER		= 6			#
	LAYER_ABOVE_PLAYER	= 8			#
	LAYER_OVERLAY		= 10		#


	def __init__(self, options=None):
		"""

		Set options, start the necessary pygame modules, instantiate Resources, create
		the "sprites" group.

		This function passes the "resource_dir" attribute when instantiating a
		Resources instance to allow it to find images and sounds. You must set this
		attribute before calling this function. If you have a "resources" directory
		beneath the directory containing your game, the helper function
		"set_resource_dir_from_file" can set it for you quite easily.

		The "options" argument is expected to be a dictionary, the items of which are
		set as attributes of the game during initialization. Some appropriate key/value
		pairs to pass to the __init__ function would be:

			display_depth
			fps
			fullscreen
			quiet
			resource_dump

		A typical use case would be if you used the "argparse" library to read
		command-line options, and wish to pass those options to the Game class before
		starting up modules. i.e.:

			import argparse, sys
			p = argparse.ArgumentParser()
			p.add_argument("--quiet", "-q", action="store_true", help="Don't make sound")
			p.add_argument("--fullscreen", "-f", action="store_true", help="Show fullscreen")
			options = p.parse_args()
			# Setup logging, etc...
			.
			.
			sys.exit(MyGameClass(options).run())

		"""
		Game.current = self
		if options is not None:
			for varname, value in options.__dict__.items():
				setattr(self, varname, value)
		if self.resource_dir is None: self.resource_dir = "resources"
		self.resources = Resources(self.resource_dir, self.resource_dump)
		pygame.init()
		if not self.quiet:
			pygame.mixer.pre_init(self.mixer_frequency, self.mixer_bitsize, self.mixer_channels, self.mixer_buffer)
		self.sprites = pygame.sprite.LayeredUpdates()

		# Event handler mapping.
		# Every event from the pygame documentation is mapped.
		# Each event handler in the Game class passes execution to
		# the corresponding function in the GameState class.

		self._event_handlers = {
			ACTIVEEVENT:				self._activeevent,				# 32768
			AUDIODEVICEADDED:			self._audiodeviceadded,			# 4352
			AUDIODEVICEREMOVED:			self._audiodeviceremoved,		# 4353
			CONTROLLERAXISMOTION:		self._controlleraxismotion,		# 1616
			CONTROLLERBUTTONDOWN:		self._controllerbuttondown,		# 1617
			CONTROLLERBUTTONUP:			self._controllerbuttonup,		# 1618
			CONTROLLERDEVICEADDED:		self._controllerdeviceadded,	# 1619
			CONTROLLERDEVICEREMAPPED:	self._controllerdeviceremapped,	# 1621
			CONTROLLERDEVICEREMOVED:	self._controllerdeviceremoved,	# 1620
			DROPBEGIN:					self._dropbegin,				# 4098
			DROPCOMPLETE:				self._dropcomplete,				# 4099
			DROPFILE:					self._dropfile,					# 4096
			DROPTEXT:					self._droptext,					# 4097
			FINGERDOWN:					self._fingerdown,				# 1792
			FINGERMOTION:				self._fingermotion,				# 1794
			FINGERUP:					self._fingerup,					# 1793
			JOYAXISMOTION:				self._joyaxismotion,			# 1536
			JOYBALLMOTION:				self._joyballmotion,			# 1537
			JOYBUTTONDOWN:				self._joybuttondown,			# 1539
			JOYBUTTONUP:				self._joybuttonup,				# 1540
			JOYDEVICEADDED:				self._joydeviceadded,			# 1541
			JOYDEVICEREMOVED:			self._joydeviceremoved,			# 1542
			JOYHATMOTION:				self._joyhatmotion,				# 1538
			KEYDOWN:					self._keydown,					# 768
			KEYUP:						self._keyup,					# 769
			MIDIIN:						self._midiin,					# 32771
			MIDIOUT:					self._midiout,					# 32772
			MOUSEBUTTONDOWN:			self._mousebuttondown,			# 1025
			MOUSEBUTTONUP:				self._mousebuttonup,			# 1026
			MOUSEMOTION:				self._mousemotion,				# 1024
			MOUSEWHEEL:					self._mousewheel,				# 1027
			MULTIGESTURE:				self._multigesture,				# 2050
			QUIT:						self._quit,						# 256
			SYSWMEVENT:					self._syswmevent,				# 513
			TEXTEDITING:				self._textediting,				# 770
			TEXTINPUT:					self._textinput,				# 771
			VIDEOEXPOSE:				self._videoexpose,				# 32770
			VIDEORESIZE:				self._videoresize,				# 32769
			WINDOWCLOSE:				self._windowclose,				# 32787
			WINDOWENTER:				self._windowenter,				# 32783
			WINDOWEXPOSED:				self._windowexposed,			# 32776
			WINDOWFOCUSGAINED:			self._windowfocusgained,		# 32785
			WINDOWFOCUSLOST:			self._windowfocuslost,			# 32786
			WINDOWHIDDEN:				self._windowhidden,				# 32775
			WINDOWHITTEST:				self._windowhittest,			# 32789
			WINDOWLEAVE:				self._windowleave,				# 32784
			WINDOWMAXIMIZED:			self._windowmaximized,			# 32781
			WINDOWMINIMIZED:			self._windowminimized,			# 32780
			WINDOWMOVED:				self._windowmoved,				# 32777
			WINDOWRESIZED:				self._windowresized,			# 32778
			WINDOWRESTORED:				self._windowrestored,			# 32782
			WINDOWSHOWN:				self._windowshown,				# 32774
			WINDOWSIZECHANGED:			self._windowsizechanged,		# 32779
			WINDOWTAKEFOCUS:			self._windowtakefocus			# 32788
		}

		pygame.event.set_allowed(list(self._event_handlers.keys()))

		# Fill-in the remaining timer events:
		for event_type in range(USEREVENT, NUMEVENTS + 1):
			self._event_handlers[event_type] = self.__timer_event
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

		... which is a decent place to put your "images" and "sounds" folders.
							("Use the defaults, Luke")
		"""
		self.resource_dir = os.path.join(os.path.dirname(os.path.realpath(filename)), "resources")


	def run(self):
		"""
		Run the game. The "initial_state" function is called from here, and must return
		an object of class GameState.
		"""
		self.show()
		self._state = self.initial_state()
		self._state.enter_state()	# Immediately enter state, not waiting for "_main_loop()"
		self.__next_state = None	# Clear this, as it was set in "change_state()"
		self._main_loop()
		return 0


	def show(self, background=None):
		"""
		Initilizes the screen, setting a background.
		You don't need to call this function, as it is called in Game.run(). Just make
		sure that you implement "initial_background".
		It is safe to call this function multiple times.
		"""
		if background is None:
			display_size = pygame.display.Info().current_w, pygame.display.Info().current_h
			self.background = self.initial_background(display_size)
		else:
			self.background = background
		self.screen_rect = self.background.get_rect()
		if self.fullscreen:
			self.display_flags |= (FULLSCREEN | SCALED)
		else:
			os.environ['SDL_VIDEO_CENTERED'] = '1'
		if self.icon is not None:
			pygame.display.set_icon(pygame.image.load(os.path.join(self.resources.image_folder, self.icon)))
		pygame.display.set_caption(self.caption)
		self.screen = pygame.display.set_mode(
			self.screen_rect.size,
			self.display_flags,
			pygame.display.mode_ok(self.screen_rect.size, self.display_flags, self.display_depth)
		)
		self.screen.blit(self.background, (0,0))
		pygame.display.flip()


	def shutdown(self):
		"""
		Triggers the _main_loop to exit. The _main_loop will finish its current
		iteration before doing so.
		"""
		self._stay_in_loop = False


	def change_state(self, game_state):
		"""
		Lines up the next game state. The next time through main_loop, the new state
		will be current.

		It is possible that this function will be called more than once during a single
		game loop cycle. For example, a player might make a move and transition to a
		game state which waits for the opponent to move, at almost the same time as
		receiving a message from their opponent that they left the game.

		In such circumstances, the last call to this function takes precedence - with
		one caveat. If any game state subclasses GameStateFinal, the game state may not
		be changed at all.
		"""
		if isinstance(self.__next_state, GameStateFinal):
			logging.warn("Changing game state when current state is GameStateFinal is not allowed")
		else:
			self.__next_state = game_state


	##################################################################################################################

	def _main_loop(self):
		self.clock = pygame.time.Clock()
		while self._stay_in_loop:
			self._state.loop_start()
			for event in pygame.event.get():
				self._event_handlers[event.type](event)
			self._end_loop()
			self.sprites.update()
			self.sprites.clear(self.screen, self.background)
			pygame.display.update(self.sprites.draw(self.screen))
			if self.__next_state:
				self._state.exit_state(self.__next_state);
				self._state = self.__next_state
				self.__next_state = None	# MUST clear __next_state before calling "enter_state()", in case
				self._state.enter_state()	# enter_state() calls "change_state()" and lines up a new "__next_state"
			self.clock.tick(self.fps)
		for cls in self.__class__.mro():
			if "exit_loop" in cls.__dict__:
				cls.exit_loop(self)


	##################################################################################################################


	def _end_loop(self):
		"""
		Called at the end of the _main_loop().
		The default implementation is to call "loop_end()" on the current GameState.
		This behaviour is overridden in NetworkGame in order to handle message transfer.
		"""
		self._state.loop_end()


	def exit_loop(self):
		"""
		Called when _main_loop() exits, after the final round of moving sprites and
		updating the display.
		"""
		pass


	# Event handlers:

	def _activeevent(self, event):
		self._state.activeevent(event)

	def _audiodeviceadded(self, event):
		self._state.audiodeviceadded(event)

	def _audiodeviceremoved(self, event):
		self._state.audiodeviceremoved(event)

	def _controlleraxismotion(self, event):
		self._state.controlleraxismotion(event)

	def _controllerbuttondown(self, event):
		self._state.controllerbuttondown(event)

	def _controllerbuttonup(self, event):
		self._state.controllerbuttonup(event)

	def _controllerdeviceadded(self, event):
		self._state.controllerdeviceadded(event)

	def _controllerdeviceremapped(self, event):
		self._state.controllerdeviceremapped(event)

	def _controllerdeviceremoved(self, event):
		self._state.controllerdeviceremoved(event)

	def _dropbegin(self, event):
		self._state.dropbegin(event)

	def _dropcomplete(self, event):
		self._state.dropcomplete(event)

	def _dropfile(self, event):
		self._state.dropfile(event)

	def _droptext(self, event):
		self._state.droptext(event)

	def _fingerdown(self, event):
		self._state.fingerdown(event)

	def _fingermotion(self, event):
		self._state.fingermotion(event)

	def _fingerup(self, event):
		self._state.fingerup(event)

	def _joyaxismotion(self, event):
		self._state.joyaxismotion(event)

	def _joyballmotion(self, event):
		self._state.joyballmotion(event)

	def _joybuttondown(self, event):
		self._state.joybuttondown(event)

	def _joybuttonup(self, event):
		self._state.joybuttonup(event)

	def _joydeviceadded(self, event):
		self._state.joydeviceadded(event)

	def _joydeviceremoved(self, event):
		self._state.joydeviceremoved(event)

	def _joyhatmotion(self, event):
		self._state.joyhatmotion(event)

	def _keydown(self, event):
		self._state.keydown(event)

	def _keyup(self, event):
		self._state.keyup(event)

	def _midiin(self, event):
		self._state.midiin(event)

	def _midiout(self, event):
		self._state.midiout(event)

	def _mousebuttondown(self, event):
		self._state.mousebuttondown(event)

	def _mousebuttonup(self, event):
		self._state.mousebuttonup(event)

	def _mousemotion(self, event):
		self._state.mousemotion(event)

	def _mousewheel(self, event):
		self._state.mousewheel(event)

	def _multigesture(self, event):
		self._state.multigesture(event)

	def _quit(self, event):
		self._state.quit(event)

	def _syswmevent(self, event):
		self._state.syswmevent(event)

	def _textediting(self, event):
		self._state.textediting(event)

	def _textinput(self, event):
		self._state.textinput(event)

	def _videoexpose(self, event):
		self._state.videoexpose(event)

	def _videoresize(self, event):
		self._state.videoresize(event)

	def _windowclose(self, event):
		self._state.windowclose(event)

	def _windowenter(self, event):
		self._state.windowenter(event)

	def _windowexposed(self, event):
		self._state.windowexposed(event)

	def _windowfocusgained(self, event):
		self._state.windowfocusgained(event)

	def _windowfocuslost(self, event):
		self._state.windowfocuslost(event)

	def _windowhidden(self, event):
		self._state.windowhidden(event)

	def _windowhittest(self, event):
		self._state.windowhittest(event)

	def _windowleave(self, event):
		self._state.windowleave(event)

	def _windowmaximized(self, event):
		self._state.windowmaximized(event)

	def _windowminimized(self, event):
		self._state.windowminimized(event)

	def _windowmoved(self, event):
		self._state.windowmoved(event)

	def _windowresized(self, event):
		self._state.windowresized(event)

	def _windowrestored(self, event):
		self._state.windowrestored(event)

	def _windowshown(self, event):
		self._state.windowshown(event)

	def _windowsizechanged(self, event):
		self._state.windowsizechanged(event)

	def _windowtakefocus(self, event):
		self._state.windowtakefocus(event)



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
		pygame.time.set_timer(USEREVENT + timer_index, 0)
		self.__timer_callbacks[timer_index] = None


	def __set_timeout(self, callback, milliseconds, arguments, recur):
		for timer_index in range(8):
			if self.__timer_callbacks[timer_index] is None:
				self.__timer_callbacks[timer_index] = callback
				self.__timer_arguments[timer_index] = arguments
				self.__timer_recur_flag[timer_index] = recur
				pygame.time.set_timer(USEREVENT + timer_index, milliseconds)
				return timer_index
		raise Exception("Too many timers!")


	def __timer_event(self, event):
		"""
		Called from the pygame event pump when a timer times out.
		Executes a timer event.
		"""
		timer_index = event.type - USEREVENT	# Subtract USEREVENT constant since our indexes start with 0
		if self.__timer_callbacks[timer_index] is None:
			logging.warning("Timer event raised when corresponding callback not set")
		else:
			if len(self.__timer_arguments[timer_index]):
				self.__timer_callbacks[timer_index](self.__timer_arguments[timer_index])
			else:
				self.__timer_callbacks[timer_index]()
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
		Game.current.change_state(self)


	def enter_state(self):
		"""
		Function called when the Game transitions to this state.
		Any information needed to be passed to this GameState should be passed as
		keyword args to the constructor.
		"""
		pass


	def exit_state(self, next_state):
		"""
		Function called when the Game transitions out of this state.
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
		The "event" object has the following members:
			gain, state
		"""
		pass

	def audiodeviceadded(self, event):
		"""
		The "event" object has the following members:
			which, iscapture
		"""
		pass

	def audiodeviceremoved(self, event):
		"""
		The "event" object has the following members:
			which, iscapture
		"""
		pass

	def controlleraxismotion(self, event):
		"""
		The "event" object has the following members:
			[unknown]
		"""
		pass

	def controllerbuttondown(self, event):
		"""
		The "event" object has the following members:
			[unknown]
		"""
		pass

	def controllerbuttonup(self, event):
		"""
		The "event" object has the following members:
			[unknown]
		"""
		pass

	def controllerdeviceadded(self, event):
		"""
		The "event" object has the following members:
			device_index
		"""
		pass

	def controllerdeviceremapped(self, event):
		"""
		The "event" object has the following members:
			instance_id
		"""
		pass

	def controllerdeviceremoved(self, event):
		"""
		The "event" object has the following members:
			instance_id
		"""
		pass

	def dropbegin(self, event):
		"""
		The "event" object has the following members:
			none
		"""
		pass

	def dropcomplete(self, event):
		"""
		The "event" object has the following members:
			none
		"""
		pass

	def dropfile(self, event):
		"""
		The "event" object has the following members:
			file
		"""
		pass

	def droptext(self, event):
		"""
		The "event" object has the following members:
			text
		"""
		pass

	def fingerdown(self, event):
		"""
		The "event" object has the following members:
			touch_id, finger_id, x, y, dx, dy
		"""
		pass

	def fingermotion(self, event):
		"""
		The "event" object has the following members:
			touch_id, finger_id, x, y, dx, dy
		"""
		pass

	def fingerup(self, event):
		"""
		The "event" object has the following members:
			touch_id, finger_id, x, y, dx, dy
		"""
		pass

	def joyaxismotion(self, event):
		"""
		The "event" object has the following members:
			instance_id, axis, value
		"""
		pass

	def joyballmotion(self, event):
		"""
		The "event" object has the following members:
			instance_id, ball, rel
		"""
		pass

	def joybuttondown(self, event):
		"""
		The "event" object has the following members:
			instance_id, button
		"""
		pass

	def joybuttonup(self, event):
		"""
		The "event" object has the following members:
			instance_id, button
		"""
		pass

	def joydeviceadded(self, event):
		"""
		The "event" object has the following members:
			device_index
		"""
		pass

	def joydeviceremoved(self, event):
		"""
		The "event" object has the following members:
			instance_id
		"""
		pass

	def joyhatmotion(self, event):
		"""
		The "event" object has the following members:
			instance_id, hat, value
		"""
		pass

	def keydown(self, event):
		"""
		The "event" object has the following members:
			key, mod, unicode, scancode
		"""
		pass

	def keyup(self, event):
		"""
		The "event" object has the following members:
			key, mod
		"""
		pass

	def midiin(self, event):
		"""
		The "event" object has the following members:
			none
		"""
		pass

	def midiout(self, event):
		"""
		The "event" object has the following members:
			none
		"""
		pass

	def mousebuttondown(self, event):
		"""
		The "event" object has the following members:
			pos, button
		"""
		pass

	def mousebuttonup(self, event):
		"""
		The "event" object has the following members:
			pos, button
		"""
		pass

	def mousemotion(self, event):
		"""
		The "event" object has the following members:
			pos, rel, buttons
		"""
		pass

	def mousewheel(self, event):
		"""
		The "event" object has the following members:
			which, flipped, x, y
		"""
		pass

	def multigesture(self, event):
		"""
		The "event" object has the following members:
			touch_id, x, y, pinched, rotated, num_fingers
		"""
		pass

	def quit(self, event):
		"""
		The "event" object has the following members:
			none
		"""
		pass

	def syswmevent(self, event):
		"""
		The "event" object has the following members:
			[unknown]
		"""
		pass

	def textediting(self, event):
		"""
		The "event" object has the following members:
			text, start, length
		"""
		pass

	def textinput(self, event):
		"""
		The "event" object has the following members:
			text
		"""
		pass

	def videoexpose(self, event):
		"""
		The "event" object has the following members:
			none
		"""
		pass

	def videoresize(self, event):
		"""
		The "event" object has the following members:
			size, w, h
		"""
		pass

	def windowclose(self, event):
		"""
		The "event" object has the following members:
			[unknown]
		"""
		pass

	def windowenter(self, event):
		"""
		The "event" object has the following members:
			[unknown]
		"""
		pass

	def windowexposed(self, event):
		"""
		The "event" object has the following members:
			[unknown]
		"""
		pass

	def windowfocusgained(self, event):
		"""
		The "event" object has the following members:
			[unknown]
		"""
		pass

	def windowfocuslost(self, event):
		"""
		The "event" object has the following members:
			[unknown]
		"""
		pass

	def windowhidden(self, event):
		"""
		The "event" object has the following members:
			[unknown]
		"""
		pass

	def windowhittest(self, event):
		"""
		The "event" object has the following members:
			[unknown]
		"""
		pass

	def windowleave(self, event):
		"""
		The "event" object has the following members:
			[unknown]
		"""
		pass

	def windowmaximized(self, event):
		"""
		The "event" object has the following members:
			[unknown]
		"""
		pass

	def windowminimized(self, event):
		"""
		The "event" object has the following members:
			[unknown]
		"""
		pass

	def windowmoved(self, event):
		"""
		The "event" object has the following members:
			[unknown]
		"""
		pass

	def windowresized(self, event):
		"""
		The "event" object has the following members:
			[unknown]
		"""
		pass

	def windowrestored(self, event):
		"""
		The "event" object has the following members:
			[unknown]
		"""
		pass

	def windowshown(self, event):
		"""
		The "event" object has the following members:
			[unknown]
		"""
		pass

	def windowsizechanged(self, event):
		"""
		The "event" object has the following members:
			[unknown]
		"""
		pass

	def windowtakefocus(self, event):
		"""
		The "event" object has the following members:
			[unknown]
		"""
		pass



class GameStateFinal(GameState):
	"""
	Final GameState; cannot be replaced even if a new GameState is instantiated
	after this one. See exit_states.py for an example.
	"""
	pass



