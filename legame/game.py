#  legame/game.py
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
Provides the Game and GameState classes, a framework for writing games.
"""
import os, logging
import pygame
try:
	from pygame.locals import FULLSCREEN, SCALED, DOUBLEBUF, USEREVENT, NUMEVENTS
except ImportError:
	from pygame import FULLSCREEN, DOUBLEBUF, USEREVENT, NUMEVENTS
	SCALED = 0
from pygame.event import event_name
from pygame import Surface
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
	resource_dump		= False		# Resources debugging mode; load filenames instead of files

	# resource manager settings:
	resource_dir		= None		# Directory where game data is located,
									# should contain subfolders "images" and "sounds"
									# See "set_resource_dir_from_file(__file__)"
	# display settings:
	fps 				= 60
	display_flags		= DOUBLEBUF
	display_depth		= 32
	caption				= ""
	icon				= None

	# sound settings:
	mixer_frequency		= 44100
	mixer_bitsize		= -16
	mixer_channels		= 8
	mixer_buffer		= 512

	# game objects:
	screen_rect			= None
	background			= None
	screen				= None
	sprites				= None
	resources			= None

	# timer options:
	max_timers			= 8

	# internal state management:
	_state				= None		# It's pretty important to keep this managed, hence, it's "protected"
	_stay_in_loop		= True		# Setting this to "False" exits the game, calling "exit_loop()"
	_next_state		= None		# Next game state waiting for change at end of main loop

	LAYER_BG			= 1			#
	LAYER_ABOVE_BG		= 2			#
	LAYER_BELOW_PLAYER	= 4			# Sprite layers
	LAYER_PLAYER		= 6			#
	LAYER_ABOVE_PLAYER	= 8			#
	LAYER_OVERLAY		= 10		#

	def __init__(self, options = None):
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

			import argparse
			p = argparse.ArgumentParser()
			p.add_argument("--quiet", "-q", action = "store_true", help = "Don't make sound")
			p.add_argument("--fullscreen", "-f", action = "store_true", help = "Show fullscreen")
			options = p.parse_args()
			# Setup logging, etc...
			.
			.
			p.exit(MyGameClass(options).run())

		"""
		Game.current = self
		if options is not None:
			for varname, value in options.__dict__.items():
				setattr(self, varname, value)
		if self.resource_dir is None:
			self.resource_dir = "resources"
		self.resources = Resources(self.resource_dir, self.resource_dump)
		if not self.quiet:
			pygame.mixer.pre_init(self.mixer_frequency, self.mixer_bitsize,
			self.mixer_channels, self.mixer_buffer)
		pygame.init()
		self.sprites = pygame.sprite.LayeredUpdates()

		# Event handler mapping.
		self._event_handlers = dict([
			(getattr(pygame.locals, const), getattr(self, '_evt_' + const.lower())) \
			for const in dir(pygame.locals) \
			if hasattr(self, '_evt_' + const.lower())])

		# Fill-in the remaining timer events:
		for event_type in range(USEREVENT, NUMEVENTS + 1):
			self._event_handlers[event_type] = self.__timer_event
		self.__timer_callbacks = [None for x in range(self.max_timers)]
		self.__timer_arguments = [None for x in range(self.max_timers)]
		self.__timer_recur_flag = [None for x in range(self.max_timers)]

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
		logging.debug('set resource dir to %s', self.resource_dir)

	def run(self):
		"""
		Run the game. The "initial_state" function is called from here, and must return
		an object of class GameState.
		"""
		self.show()
		self._state = self.initial_state()
		self._state.enter_state()	# Immediately enter state, not waiting for "_main_loop()"
		self._next_state = None	# Clear this, as it was set in "change_state()"
		self._main_loop()
		return 0

	def show(self):
		"""
		Initilizes the screen.

		Make sure that you implement "initial_background", as that is what will be shown.

		It is safe to call this function multiple times.
		"""
		display_size = pygame.display.Info().current_w, pygame.display.Info().current_h
		self.background = self.initial_background(display_size)
		self.screen_rect = self.background.get_rect()
		if self.fullscreen:
			self.display_flags |= (FULLSCREEN | SCALED)
		else:
			os.environ['SDL_VIDEO_CENTERED'] = '1'
		if self.icon is not None:
			pygame.display.set_icon(pygame.image.load(os.path.join(
				self.resources.image_folder, self.icon)))
		pygame.display.set_caption(self.caption)
		self.screen = pygame.display.set_mode(
			self.screen_rect.size,
			self.display_flags,
			pygame.display.mode_ok(self.screen_rect.size, self.display_flags, self.display_depth)
		)
		self.screen.blit(self.background, (0,0))
		pygame.display.flip()

	def initial_background(self, display_size):
		"""
		Returns a pygame.Surface to use to fill the screen at startup.
		"""
		return Surface(display_size)

	def initial_state(self):
		"""
		Returns a GameState object which will take over as soon as the game is initialized.
		"""
		return GameState()

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
		if isinstance(self._next_state, GameStateFinal):
			logging.warning("Cannot change game state when current state is GameStateFinal")
		else:
			self._next_state = game_state

	###############################################################################################

	def _main_loop(self):
		clock = pygame.time.Clock()
		while self._stay_in_loop:
			self._state.loop_start()
			for event in pygame.event.get():
				try:
					self._event_handlers[event.type](event)
				except KeyError:
					logging.warning('Unknown event "%s"', event_name(event.type))

			self._end_loop()
			self.sprites.update()
			self.sprites.clear(self.screen, self.background)
			pygame.display.update(self.sprites.draw(self.screen))
			if self._next_state:
				self._state.exit_state(self._next_state)
				self._state = self._next_state
				self._next_state = None
				self._state.enter_state()
			clock.tick(self.fps)
		for cls in self.__class__.mro():
			if "exit_loop" in cls.__dict__:
				cls.exit_loop(self)

	###############################################################################################

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

	# Event handlers:

	def _evt_activeevent(self, event):
		self._state.active_event(event)

	def _evt_audiodeviceadded(self, event):
		self._state.audio_device_added(event)

	def _evt_audiodeviceremoved(self, event):
		self._state.audio_device_removed(event)

	def _evt_controlleraxismotion(self, event):
		self._state.controller_axis_motion(event)

	def _evt_controllerbuttondown(self, event):
		self._state.controller_button_down(event)

	def _evt_controllerbuttonup(self, event):
		self._state.controller_button_up(event)

	def _evt_controllerdeviceadded(self, event):
		self._state.controller_device_added(event)

	def _evt_controllerdeviceremapped(self, event):
		self._state.controller_device_remapped(event)

	def _evt_controllerdeviceremoved(self, event):
		self._state.controller_device_removed(event)

	def _evt_dropbegin(self, event):
		self._state.drop_begin_event(event)

	def _evt_dropcomplete(self, event):
		self._state.drop_complete_event(event)

	def _evt_dropfile(self, event):
		self._state.drop_file_event(event)

	def _evt_droptext(self, event):
		self._state.drop_text_event(event)

	def _evt_fingerdown(self, event):
		self._state.finger_down(event)

	def _evt_fingermotion(self, event):
		self._state.finger_motion(event)

	def _evt_fingerup(self, event):
		self._state.finger_up(event)

	def _evt_joyaxismotion(self, event):
		self._state.joy_axis_motion(event)

	def _evt_joyballmotion(self, event):
		self._state.joy_ball_motion(event)

	def _evt_joybuttondown(self, event):
		self._state.joy_button_down(event)

	def _evt_joybuttonup(self, event):
		self._state.joy_button_up(event)

	def _evt_joydeviceadded(self, event):
		self._state.joy_device_added(event)

	def _evt_joydeviceremoved(self, event):
		self._state.joy_device_removed(event)

	def _evt_joyhatmotion(self, event):
		self._state.joy_hat_motion(event)

	def _evt_keydown(self, event):
		self._state.key_down(event)

	def _evt_keyup(self, event):
		self._state.key_up(event)

	def _evt_midiin(self, event):
		self._state.midi_in(event)

	def _evt_midiout(self, event):
		self._state.midi_out(event)

	def _evt_mousebuttondown(self, event):
		self._state.mouse_button_down(event)

	def _evt_mousebuttonup(self, event):
		self._state.mouse_button_up(event)

	def _evt_mousemotion(self, event):
		self._state.mouse_motion(event)

	def _evt_mousewheel(self, event):
		self._state.mouse_wheel(event)

	def _evt_multigesture(self, event):
		self._state.multi_gesture_event(event)

	def _evt_quit(self, event):
		self._state.quit_event(event)

	def _evt_syswmevent(self, event):
		self._state.sys_wm_event(event)

	def _evt_textediting(self, event):
		self._state.text_editing_event(event)

	def _evt_textinput(self, event):
		self._state.text_input_event(event)

	def _evt_videoexpose(self, event):
		self._state.video_expose(event)

	def _evt_videoresize(self, event):
		self._state.video_resize(event)

	def _evt_windowclose(self, event):
		self._state.window_close_event(event)

	def _evt_windowenter(self, event):
		self._state.window_enter(event)

	def _evt_windowexposed(self, event):
		self._state.window_exposed(event)

	def _evt_windowfocusgained(self, event):
		self._state.window_focus_gained(event)

	def _evt_windowfocuslost(self, event):
		self._state.window_focus_lost(event)

	def _evt_windowhidden(self, event):
		self._state.window_hidden(event)

	def _evt_windowhittest(self, event):
		self._state.window_hit_test(event)

	def _evt_windowleave(self, event):
		self._state.window_leave(event)

	def _evt_windowmaximized(self, event):
		self._state.window_maximized(event)

	def _evt_windowminimized(self, event):
		self._state.window_minimized(event)

	def _evt_windowmoved(self, event):
		self._state.window_moved(event)

	def _evt_windowresized(self, event):
		self._state.window_resized(event)

	def _evt_windowrestored(self, event):
		self._state.window_restored(event)

	def _evt_windowshown(self, event):
		self._state.window_shown(event)

	def _evt_windowsizechanged(self, event):
		self._state.window_size_changed(event)

	def _evt_windowtakefocus(self, event):
		self._state.window_take_focus(event)

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
		for timer_index in range(self.max_timers):
			if self.__timer_callbacks[timer_index] is None:
				self.__timer_callbacks[timer_index] = callback
				self.__timer_arguments[timer_index] = arguments
				self.__timer_recur_flag[timer_index] = recur
				pygame.time.set_timer(USEREVENT + timer_index, milliseconds)
				return timer_index
		raise RuntimeError("Too many timers!")

	def __timer_event(self, event):
		"""
		Called from the pygame event pump when a timer times out.
		Executes a timer event.
		"""
		timer_index = event.type - USEREVENT	# Subtract USEREVENT constant; indexes start with 0
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
		if not self.quiet:
			self.resources.sound(sound_name).play()


class GameState:

	def __init__(self, **kwargs):
		"""
		Set up this GameState to be the new game state next time through the main loop.
		The new state will have attributes set by keyword args passed to this function.
		If the current game state is an instance of "GameStateFinal", the current game
		state will not be changed.
		"""
		for varname, value in kwargs.items():
			setattr(self, varname, value)
		Game.current.change_state(self)

	def enter_state(self):
		"""
		Function called when the Game transitions to this state.
		Any information needed to be passed to this GameState should be passed as
		keyword args to the constructor.
		"""

	def exit_state(self, next_state):
		"""
		Function called when the Game transitions out of this state.
		The "next_state" parameter is the GameState object which will replace this one.
		"""

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

	# Event handlers called from Game._main_loop():

	def active_event(self, event):
		"""
		The "event" object has the following members:
			gain, state
		"""

	def audio_device_added(self, event):
		"""
		The "event" object has the following members:
			which, iscapture
		"""

	def audio_device_removed(self, event):
		"""
		The "event" object has the following members:
			which, iscapture
		"""

	def controller_axis_motion(self, event):
		"""
		The "event" object has the following members:
			[unknown]
		"""

	def controller_button_down(self, event):
		"""
		The "event" object has the following members:
			[unknown]
		"""

	def controller_button_up(self, event):
		"""
		The "event" object has the following members:
			[unknown]
		"""

	def controller_device_added(self, event):
		"""
		The "event" object has the following members:
			device_index
		"""

	def controller_device_remapped(self, event):
		"""
		The "event" object has the following members:
			instance_id
		"""

	def controller_device_removed(self, event):
		"""
		The "event" object has the following members:
			instance_id
		"""

	def drop_begin_event(self, event):
		"""
		The "event" object has the following members:
			none
		"""

	def drop_complete_event(self, event):
		"""
		The "event" object has the following members:
			none
		"""

	def drop_file_event(self, event):
		"""
		The "event" object has the following members:
			file
		"""

	def drop_text_event(self, event):
		"""
		The "event" object has the following members:
			text
		"""

	def finger_down(self, event):
		"""
		The "event" object has the following members:
			touch_id, finger_id, x, y, dx, dy
		"""

	def finger_motion(self, event):
		"""
		The "event" object has the following members:
			touch_id, finger_id, x, y, dx, dy
		"""

	def finger_up(self, event):
		"""
		The "event" object has the following members:
			touch_id, finger_id, x, y, dx, dy
		"""

	def joy_axis_motion(self, event):
		"""
		The "event" object has the following members:
			instance_id, axis, value
		"""

	def joy_ball_motion(self, event):
		"""
		The "event" object has the following members:
			instance_id, ball, rel
		"""

	def joy_button_down(self, event):
		"""
		The "event" object has the following members:
			instance_id, button
		"""

	def joy_button_up(self, event):
		"""
		The "event" object has the following members:
			instance_id, button
		"""

	def joy_device_added(self, event):
		"""
		The "event" object has the following members:
			device_index
		"""

	def joy_device_removed(self, event):
		"""
		The "event" object has the following members:
			instance_id
		"""

	def joy_hat_motion(self, event):
		"""
		The "event" object has the following members:
			instance_id, hat, value
		"""

	def key_down(self, event):
		"""
		The "event" object has the following members:
			key, mod, unicode, scancode
		"""

	def key_up(self, event):
		"""
		The "event" object has the following members:
			key, mod
		"""

	def midi_in(self, event):
		"""
		The "event" object has the following members:
			none
		"""

	def midi_out(self, event):
		"""
		The "event" object has the following members:
			none
		"""

	def mouse_button_down(self, event):
		"""
		The "event" object has the following members:
			pos, button
		"""

	def mouse_button_up(self, event):
		"""
		The "event" object has the following members:
			pos, button
		"""

	def mouse_motion(self, event):
		"""
		The "event" object has the following members:
			pos, rel, buttons
		"""

	def mouse_wheel(self, event):
		"""
		The "event" object has the following members:
			which, flipped, x, y
		"""

	def multi_gesture_event(self, event):
		"""
		The "event" object has the following members:
			touch_id, x, y, pinched, rotated, num_fingers
		"""

	def quit_event(self, event):
		"""
		The "event" object has the following members:
			none
		"""

	def sys_wm_event(self, event):
		"""
		The "event" object has the following members:
			[unknown]
		"""

	def text_editing_event(self, event):
		"""
		The "event" object has the following members:
			text, start, length
		"""

	def text_input_event(self, event):
		"""
		The "event" object has the following members:
			text
		"""

	def video_expose(self, event):
		"""
		The "event" object has the following members:
			none
		"""

	def video_resize(self, event):
		"""
		The "event" object has the following members:
			size, w, h
		"""

	def window_close_event(self, event):
		"""
		The "event" object has the following members:
			[unknown]
		"""

	def window_enter(self, event):
		"""
		The "event" object has the following members:
			[unknown]
		"""

	def window_exposed(self, event):
		"""
		The "event" object has the following members:
			[unknown]
		"""

	def window_focus_gained(self, event):
		"""
		The "event" object has the following members:
			[unknown]
		"""

	def window_focus_lost(self, event):
		"""
		The "event" object has the following members:
			[unknown]
		"""

	def window_hidden(self, event):
		"""
		The "event" object has the following members:
			[unknown]
		"""

	def window_hit_test(self, event):
		"""
		The "event" object has the following members:
			[unknown]
		"""

	def window_leave(self, event):
		"""
		The "event" object has the following members:
			[unknown]
		"""

	def window_maximized(self, event):
		"""
		The "event" object has the following members:
			[unknown]
		"""

	def window_minimized(self, event):
		"""
		The "event" object has the following members:
			[unknown]
		"""

	def window_moved(self, event):
		"""
		The "event" object has the following members:
			[unknown]
		"""

	def window_resized(self, event):
		"""
		The "event" object has the following members:
			[unknown]
		"""

	def window_restored(self, event):
		"""
		The "event" object has the following members:
			[unknown]
		"""

	def window_shown(self, event):
		"""
		The "event" object has the following members:
			[unknown]
		"""

	def window_size_changed(self, event):
		"""
		The "event" object has the following members:
			[unknown]
		"""

	def window_take_focus(self, event):
		"""
		The "event" object has the following members:
			[unknown]
		"""


class GameStateFinal(GameState):
	"""
	Final GameState; cannot be replaced even if a new GameState is instantiated
	after this one. See exit_states.py for an example.
	"""


#  end legame/game.py
