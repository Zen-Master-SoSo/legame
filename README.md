# LeGame

Modules which aid in creating 2-dimensional games with pygame.

## Intro

Playing around with pygame, I quickly found that I was doing the same thing over and over again. I figured it'd be a good idea to make a template for a game and reuse it. That quickly devolved to an obsession with making a whole game framework, with pieces and parts which all fit together and makes everything easy. And that's what eventually led to "LeGame".

Here's a quick rundown on what's included (so far) and what each part does:

| module             | What it does                                                                        |
|--------------------|-------------------------------------------------------------------------------------|
| game               | Framework with main loop, events, easy-to-use timers, state management              |
| board_game         | Basic framework for games with pieces on squares (like chess, checkers, etc.)       |
| network_game       | Create a game which is played over a network                                        |
| joiner             | Discover / connect with another computer over the network using a dialog            |
| sprite_enhancement | Add motion to sprites; position sprites using their center point; boundary checking |
| resources          | Load images, sounds, and sets of images for image flipping                          |
| flipper            | Image flipping classes to animate the appearance of sprites                         |
| neighbors          | Checks which sprites are close to one another when there are lots on the screen     |
| callout            | A debugging tool that follows a sprite on screen and displays some text             |
| exit_states        | Game states which are pretty common, like "quit"                                    |
| configurable       | Simple cross-platform configuration save/restore functions                          |
| locals             | Constants and functions which are needed by some of the above modules               |

## The Rundown

Here's a quick rundown so you can decide if this framework is right for you.

### States

Any game written for pygame has a "main loop", and checks events in the loop. The main_loop function of the "Game" class is extremely minimal, dispatching (almost) all of the events to be handled to a GameState class.

The base GameState class has a function, or "handler", for each of the possible event types that pygame produces. For example, there are GameState functions named "keydown", "mousedown", and "loop_end". In the base GameState class, they're empty. If you need to handle these events, you put the logic for your game in those handlers.

I wrote a space rescue game with a single game state: "GsPlay", and that was sufficient. A board game, in contrast has more states and managing them is actually more complicated.

### Sprites

The "sprite_enhancement" module includes the "MovingSprite" class which aids in moving sprites around the screen. Each sprite has a "position" and "motion" property, each a Vector, which are used to update the position each time through the event loop. The "flipper" module provides classes which flip the image of a sprite on a cyclical basis, in two differen modes.

Any sprite in your game can also inherit "MovingSprite", and can also inherit "Flipper". Inherit both and you've got a pretty fancy little animated moving thing, with very little necessary coding.

The flipper module makes use of the "ImageSet" class of the "resources" module. An ImageSet is created by loading all of the images found in a sudirectory below your image resources directory. They're sorted when loaded, and this sequence of images are flipped on a regular cyclical basis to create an animation.

### Timers

Timers in pygame are a little clunky, so they're enhanced by the Game class. Pygame provides up to eight timers which are identified by their event number. When you pull events from the pygame event queue, the number pops up. You're supposed to manage the timer numbers and do something or other depending upon the number.

I like the way timers work in JavaScript. You just call "setTimeout" with a function that gets called when the timer times out. So, the Game class provides a "set_timeout" function which does the same thing. No worrying about keeping track of pygame timer event numbers, because the Game class does that for you. Implementing a timer is as simple as:

	Game.current.set_timeout(self.generate_enemy, 2500, position=(23, 37))

... and in 2500 milliseconds, "self.generate_enemy()" will be called with "position=(23, 37)" as an argument.

### Networking

The "joiner" module provides classes for connecting to a remote machine using a pygame-generated dialog. The "BroadcastJoiner" uses UDP broadcast to announce availability on the network, and you can see the other player's names and machine names to choose from. The "DirectJoiner" module allows you to connect to a specific machine, as either the "server" or the "client". Note that although the term "server" is used to describe the *way* you connect, there's nothing in the framework as of now which supports creation of a game server which multiple clients will connect to, although it's not impossible.

After a "JoinerDialog" connects to a remote machine, the NetworkGame class (a sublcass of Game) communicates with the remote machine, allowing you to send and receive Message objects. I developed the "cable_car" package to provide fast, lightweight, and easy-to-use messaging, and LeGame uses the that package for communicating across the network.

### Put it Together

Let's say you want to create a battling spaceships game to play over the network. You would create a game class which subclasses NetworkGame:

	class BattleCraft(NetworkGame):

		<snip>

There's only one GameState:

	class GSBattle(GameState):

		def enter_state(self):
			Game.current.my_ship = SpaceShip(
				Game.current.screen_rect.centerx, 50,
				Game.current.my_color
			)
			Game.current.their_ship = SpaceShip(
				Game.current.screen_rect.centerx,
				Game.current.screen_rect.centery - 50,
				Game.current.my_color
			)

		def keydown(self, event):
			if event.key == K_SPACE:
				Game.current.my_ship.thrust = True
			elif event.key == K_LEFT:
				Game.current.my_ship.rotation -= 1
			elif event.key == K_RIGHT:
				Game.current.my_ship.rotation += 1
			elif event.key == K_ENTER:
				Game.current.my_ship.shoot()

		def keyup(self, event):
			if event.key == K_SPACE:
				Game.current.my_ship.thrust = False

		def handle_message(self, message):
			if isinstance(message, MsgQuit):
				GSQuit()	# Transition to the GSQuit game state
			elif isinstance(message, ShipPosition):
				message.mirror()
				Game.current.their_ship.position = message.position
				Game.current.their_ship.rotation = message.rotation
			elif ... <you get the point>


Create some images and put them in a folder named "resources/images", off the same folder where your game is. You create sprites which use those images. That class might look like this:

	class SpaceShip(MovingSprite, Sprite):

		def __init__(self, x, y, color):
			# Set position:
			MovingSprite.__init__(self, x, y)
			self.image_set = Game.current.resources.image_set("SpaceShip/" + color)
			self.color = color

		def update(self):				# Called from Game.sprites.update()
			if self.thrust:
				self.speed = max(self.max_speed, self.speed + self.accel)
			self.image = self.image_set.images[
				math.floor(self.rotation / self.image_set.count)
			]
			self.cartesian_motion()		# Defined in the MovingSprite class
			Game.current.messenger.send(ShipPosition(self.position, self.rotation))

The above example is incomplete, but is only meant to give you an idea of how to use LeGame.

There are some real, working examples in the "examples" folder.

## Class Reference

Most of the classes are well documented in the code using python docstrings. There's a copy of pdoc -generated documentation in the "docs" folder. Hopefully, that's all you need to get going!

**Have fun!**









