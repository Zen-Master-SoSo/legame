import pytest
from pygame import Rect
from legame.board_game import *
from legame.game import Game

@pytest.fixture(autouse=True)
def game():
	return FakeGame()

class FakeGame(BoardGame):
	pass


def test_game_init():
	FakeGame()
	assert isinstance(Game.current, BoardGame)
	assert isinstance(Game.current.board, GameBoard)
	assert Game.current.board.left == 0
	assert Game.current.board.top == 0
	assert Game.current.board.cell_height == 50
	assert Game.current.board.cell_width == 50
	assert Game.current.board.cell_half_width == 25
	assert Game.current.board.cell_half_height == 25


def test_Board_cell_at():
	game = FakeGame()
	board = game.board

	with pytest.raises(ValueError) as e:
		x = board.cell_at()
	with pytest.raises(ValueError) as e:
		x = board.cell_at(())
	with pytest.raises(ValueError) as e:
		x = board.cell_at(1)
	with pytest.raises(ValueError) as e:
		x = board.cell_at((1,))
	with pytest.raises(ValueError) as e:
		x = board.cell_at(1,2,3)
	with pytest.raises(ValueError) as e:
		x = board.cell_at((1,2,3))

	cell = board.cell_at(0, 0)
	assert isinstance(cell, BoardPosition)
	assert cell.column == 0
	assert cell.row == 0
	cell = board.cell_at((0, 0))
	assert isinstance(cell, BoardPosition)
	assert cell.column == 0
	assert cell.row == 0

	# floats:

	cell = board.cell_at(25.0, 25.0)
	assert isinstance(cell, BoardPosition)
	assert cell.column == 0
	assert cell.row == 0
	cell = board.cell_at((25.0, 25.0))
	assert isinstance(cell, BoardPosition)
	assert cell.column == 0
	assert cell.row == 0

	cell = board.cell_at((1, 1))
	assert isinstance(cell, BoardPosition)
	assert cell.column == 0
	assert cell.row == 0

	cell = board.cell_at(25, 25)
	assert isinstance(cell, BoardPosition)
	assert cell.column == 0
	assert cell.row == 0

	cell = board.cell_at((26, 26))
	assert isinstance(cell, BoardPosition)
	assert cell.column == 0
	assert cell.row == 0

	cell = board.cell_at((49, 49))
	assert isinstance(cell, BoardPosition)
	assert cell.column == 0
	assert cell.row == 0

	cell = board.cell_at((50, 50))
	assert isinstance(cell, BoardPosition)
	assert cell.column == 1
	assert cell.row == 1

	cell = board.cell_at((99, 99))
	assert isinstance(cell, BoardPosition)
	assert cell.column == 1
	assert cell.row == 1

	cell = board.cell_at((100, 100))
	assert isinstance(cell, BoardPosition)
	assert cell.column == 2
	assert cell.row == 2

	# test outside board

	cell = board.cell_at(-1, 0)
	assert cell is None

	cell = board.cell_at(0, -1)
	assert cell is None

	cell = board.cell_at(board.rect.width + 1, 0)
	assert cell is None

	cell = board.cell_at(0, board.rect.height + 1)
	assert cell is None



def test_BoardPosition_get_rect():
	game = FakeGame()
	board = game.board

	cell = board.cell_at(0, 0)
	assert isinstance(cell, BoardPosition)
	assert cell.column == 0
	assert cell.row == 0
	rect = cell.get_rect()
	assert isinstance(rect, Rect)
	assert rect.x == 0
	assert rect.y == 0
	assert rect.width == game.board.cell_width
	assert rect.height == game.board.cell_height

	cell = board.cell_at(75, 75)
	assert isinstance(cell, BoardPosition)
	assert cell.column == 1
	assert cell.row == 1
	rect = cell.get_rect()
	assert isinstance(rect, Rect)
	assert rect.x == game.board.cell_width
	assert rect.y == game.board.cell_height
	assert rect.width == game.board.cell_width
	assert rect.height == game.board.cell_height



