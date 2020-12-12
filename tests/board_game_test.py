import pytest
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


def test_BoardPosition_from_screen_pos():
	FakeGame()
	with pytest.raises(ValueError) as e:
		x = BoardPosition.from_screen_pos()
	with pytest.raises(ValueError) as e:
		x = BoardPosition.from_screen_pos(())
	with pytest.raises(ValueError) as e:
		x = BoardPosition.from_screen_pos(1)
	with pytest.raises(ValueError) as e:
		x = BoardPosition.from_screen_pos((1,))
	with pytest.raises(ValueError) as e:
		x = BoardPosition.from_screen_pos(1,2,3)
	with pytest.raises(ValueError) as e:
		x = BoardPosition.from_screen_pos((1,2,3))

	pos = BoardPosition.from_screen_pos(0, 0)
	assert isinstance(pos, BoardPosition)
	assert pos.column == 0
	assert pos.row == 0
	pos = BoardPosition.from_screen_pos((0, 0))
	assert isinstance(pos, BoardPosition)
	assert pos.column == 0
	assert pos.row == 0

	pos = BoardPosition.from_screen_pos(25.0, 25.0)
	assert isinstance(pos, BoardPosition)
	assert pos.column == 0
	assert pos.row == 0
	pos = BoardPosition.from_screen_pos((25.0, 25.0))
	assert isinstance(pos, BoardPosition)
	assert pos.column == 0
	assert pos.row == 0

	pos = BoardPosition.from_screen_pos((1, 1))
	assert isinstance(pos, BoardPosition)
	assert pos.column == 0
	assert pos.row == 0

	pos = BoardPosition.from_screen_pos(25, 25)
	assert isinstance(pos, BoardPosition)
	assert pos.column == 0
	assert pos.row == 0

	pos = BoardPosition.from_screen_pos((26, 26))
	assert isinstance(pos, BoardPosition)
	assert pos.column == 0
	assert pos.row == 0

	pos = BoardPosition.from_screen_pos((49, 49))
	assert isinstance(pos, BoardPosition)
	assert pos.column == 0
	assert pos.row == 0

	pos = BoardPosition.from_screen_pos((50, 50))
	assert isinstance(pos, BoardPosition)
	assert pos.column == 1
	assert pos.row == 1

	pos = BoardPosition.from_screen_pos((99, 99))
	assert isinstance(pos, BoardPosition)
	assert pos.column == 1
	assert pos.row == 1

	pos = BoardPosition.from_screen_pos((100, 100))
	assert isinstance(pos, BoardPosition)
	assert pos.column == 2
	assert pos.row == 2



