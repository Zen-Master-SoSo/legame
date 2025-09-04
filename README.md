# LeGame

Modules which aid in creating 2-dimensional games with pygame.

## Intro

Playing around with pygame, I quickly found that I was doing the same thing over and over again. I figured it'd be a good idea to make a template for a game and reuse it. That quickly devolved to an obsession with making a whole game framework, with pieces and parts which all fit together and makes everything easy. And that's what eventually led to "LeGame".

Here's what's included (so far) and what each part does:

| module             | What it does                                                                        |
|--------------------|-------------------------------------------------------------------------------------|
| game               | Framework with main loop, events, easy-to-use timers, state management              |
| board_game         | Basic framework for games with pieces on squares (like chess, checkers, etc.)       |
| network_game       | Create a game which is played over a network                                        |
| joiner             | Discover / connect with another computer over the network using a dialog            |
| sprite_enhancement | Add motion to sprites; position sprites using their center point; boundary checking |
| resources          | Load images, sounds, and sets of images for image flipping                          |
| flipper            | Image flipping classes to animate the appearance of sprites                         |
| neighbors          | Checks which sprites are close to one another when there many on the screen         |
| callout            | A debugging tool that follows a sprite on screen and displays some text             |
| exit_states        | Game states which are commonly used (See GameState below)                           |
| configurable       | Simple cross-platform configuration save/restore functions                          |
| locals             | Constants and functions which are needed by some of the above modules               |

## Key classes / concepts

#### Game

The Game class intializes everything, incuding the inital background and the
screen, and provides the main loop, as well as timer maintenance. The main_loop
function of the "Game" class is extremely minimal however. Almost all events
are dispatched to a GameState class for handling.

#### GameState

The base GameState class has a function, or "handler", for each of the possible
event types that pygame produces, except for timers. For example, there are
GameState functions for "keydown", "mousedown", and "quit" events. In the base
GameState class, they're empty. When you need to handle these events, you
subclass GameState and write the event handlers you need in there.

Your game can have more than one state, where what happens in response to
pygame events are different in different states. You can change how your game
responds to events by changing the current game state to one with a different
set of handlers defined. All you need to do is instantiate a new GameState and
the transition happens automatically. When it does, the old state has its
"exit_state()" function called, and the new state gets "enter_state()".

It's possible to have just one game state. I wrote a space rescue game with a
single game state, "GSPlay", and that was sufficient. A board game I wrote, in
contrast, had a lot more states and managing them was actually a lot more
complicated.

#### Sprites

The "sprite_enhancement" module includes the "MovingSprite" class which aids in
moving sprites around the screen. Each sprite has a "position" and "motion"
property which are used to update the position each time through the event loop.

The "flipper" module provides classes which flip the image of a sprite on a
cyclical basis. Any sprite in your game which inherits Sprite can also inherit
both "MovingSprite" and "Flipper". Inherit both "MovingSprite" and "Flipper"
and you've got a pretty fancy little animated moving thing, with very little
coding necessary.

#### Resources

The flipper module uses the "ImageSet" class of the "resources" module to
manage images. An ImageSet is created by loading all of the images found in a
sudirectory. They're sorted when loaded, and this sequence of images are
flipped on a regular cyclical basis to create an animation.

Single images and sounds are also loaded using the Resources class, with
cross-platform support. You don't have to worry about Windows paths breaking
your code.

#### Timers

Timers in pygame are a little clunky, so I enhanced them in the Game class.
Pygame provides up to eight timers which are identified by their event number.
When you pull events from the pygame event queue, the number pops up. You're
supposed to keep track of these numbers and do something or other depending
upon what pops out.

I like the way timers work in JavaScript. You just call "setTimeout" with a
function, and it gets called when the timer times out. So the Game class
provides a "set_timeout" function which works the same. Implementing a timer is
as simple as:

	Game.current.set_timeout(self.generate_enemy, 2500, x=53, y=137)

... and in 2500 milliseconds, "self.generate_enemy()" will be called with
"x=53" and "y=137" as arguments. No worrying about keeping track of pygame
event numbers, because the Game class does all that for you.

#### Networking

The "joiner" module provides classes for connecting to a remote machine using a
dialog rendered by pygame.

"BroadcastJoiner" uses UDP broadcast to announce over the network. You can see
the other player's user and host names and invite someone or accept an
invitation.

"DirectJoiner" allows you to connect to a specific ip address, (even the
127.0.0.1 loopback address), as either the "server" or the "client". Although
the term "server" is used to describe the *way* you connect, there's nothing in
the framework which as of now supports the creation of a game server which
multiple clients connect with. It's not impossible. You can do it, if you're so
inclined. But it's not included.

After a "JoinerDialog" connects to a remote machine, a Messenger sends Message
objects between each game instance. LeGame uses fast, lightweight, and
easy-to-use messaging provided by the "cable_car" package, which was written
specifically for this application.

## Quick start

I've provided some templates to quickly get you started on a game. You can find
them in the "templates" folder. There, you'll find the following:

* game.py
* board-game.py
* network-game.py
* network-board-game.py

## Reference

Most of the code is documented using python docstrings. It's all compiled into
pdoc -generated html, which you can find in the "docs" folder.


#### Tip on using globals:

There's some variables which would be convenient to make global. You might like
to declare them in your game module, or declare them "global" in your Game
class. Either way, remember that python will assume you're using a local
variable instead of a global if it's being assigned a value inside a function,
in which case you need to declare that it's global. I got bit by that several
times. Easy fix, but annoying.

Here's an example from a game that uses globals:

	def __init__ (self, options):
		global game, board, resources, play
		self.set_resource_dir_from_file(__file__)
		BoardGame.__init__(self, options)
		NetworkGame.__init__(self, options)
		game = self
		board = self.board
		resources = self.resources
		play = self.play

	def initial_state(self):
		global send
		send = self.messenger.send
		return GSSelectColor()


Now, to refer to the game, you use "game". To refer to the game board, use
"board". To refer to the Resources of the game, you use "resources". To play a
sound, just call "play". To send a message, use "send".

But note that you can't declare "send" in the \_\_init\_\_ function of the
game. The "messenger" which does the "send" is still "None" until the game
joiner dialog is shown and your game is actually started.  The "initial_state"
function is called after the game joiner is closed and a Messenger has been
instantiated, so it's safe to attach the global "send" token to the
"Messenger.send()" function there.


