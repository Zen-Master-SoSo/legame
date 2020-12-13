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
	assert isinstance(cell, Cell)
	assert cell.column == 0
	assert cell.row == 0
	cell = board.cell_at((0, 0))
	assert isinstance(cell, Cell)
	assert cell.column == 0
	assert cell.row == 0

	# floats:

	cell = board.cell_at(25.0, 25.0)
	assert isinstance(cell, Cell)
	assert cell.column == 0
	assert cell.row == 0
	cell = board.cell_at((25.0, 25.0))
	assert isinstance(cell, Cell)
	assert cell.column == 0
	assert cell.row == 0

	cell = board.cell_at((1, 1))
	assert isinstance(cell, Cell)
	assert cell.column == 0
	assert cell.row == 0

	cell = board.cell_at(25, 25)
	assert isinstance(cell, Cell)
	assert cell.column == 0
	assert cell.row == 0

	cell = board.cell_at((26, 26))
	assert isinstance(cell, Cell)
	assert cell.column == 0
	assert cell.row == 0

	cell = board.cell_at((49, 49))
	assert isinstance(cell, Cell)
	assert cell.column == 0
	assert cell.row == 0

	cell = board.cell_at((50, 50))
	assert isinstance(cell, Cell)
	assert cell.column == 1
	assert cell.row == 1

	cell = board.cell_at((99, 99))
	assert isinstance(cell, Cell)
	assert cell.column == 1
	assert cell.row == 1

	cell = board.cell_at((100, 100))
	assert isinstance(cell, Cell)
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



def test_Cell_get_rect():
	game = FakeGame()
	board = game.board

	cell = board.cell_at(0, 0)
	assert isinstance(cell, Cell)
	assert cell.column == 0
	assert cell.row == 0
	rect = cell.get_rect()
	assert isinstance(rect, Rect)
	assert rect.x == 0
	assert rect.y == 0
	assert rect.width == game.board.cell_width
	assert rect.height == game.board.cell_height

	cell = board.cell_at(75, 75)
	assert isinstance(cell, Cell)
	assert cell.column == 1
	assert cell.row == 1
	rect = cell.get_rect()
	assert isinstance(rect, Rect)
	assert rect.x == game.board.cell_width
	assert rect.y == game.board.cell_height
	assert rect.width == game.board.cell_width
	assert rect.height == game.board.cell_height


def test_rotate():
	game = FakeGame()
	board = game.board

	cell = Cell(0, 0)
	rot_cell = board.rotate(cell)
	assert rot_cell.column + cell.column == board.last_column
	assert rot_cell.row + cell.row == board.last_row

	cell = Cell(2, 4)
	rot_cell = board.rotate(cell)
	print(cell, rot_cell)
	assert rot_cell.column + cell.column == board.last_column
	assert rot_cell.row + cell.row == board.last_row

	cell = Cell(board.center_column, board.center_row)
	rot_cell = board.rotate(cell)
	assert rot_cell.column + cell.column == board.last_column
	assert rot_cell.row + cell.row == board.last_row


def test_cell_access():
	game = FakeGame()
	board = game.board

	cell = Cell(0, 0)
	piece = board.piece_at(cell)
	assert piece is None
	board.set_cell(cell, AbstractGamePiece(cell, "r"))
	piece = board.piece_at(cell)
	assert isinstance(piece, AbstractGamePiece)
	assert piece.color == "r"

	cell = Cell(0, 1)
	piece = cell.piece()
	assert piece is None
	board.set_cell(cell, AbstractGamePiece(cell, "r"))
	piece = cell.piece()
	assert isinstance(piece, AbstractGamePiece)
	assert piece.color == "r"


def test_column_row_access():
	game = FakeGame()
	board = game.board

	cells = board.column(0)
	assert isinstance(cells, list)
	assert len(cells) == board.rows

	cells = board.row(0)
	assert isinstance(cells, list)
	assert len(cells) == board.columns

	cell = Cell(0, 0)
	board.set_cell(cell, AbstractGamePiece(cell, "r"))
	cells = board.row(cell.row)
	assert isinstance(cells[0], AbstractGamePiece)
	for cell in cells[1:]: assert cell is None

	cell = Cell(0, 0)
	board.set_cell(cell, AbstractGamePiece(cell, "r"))
	cells = board.column(cell.column)
	assert isinstance(cells[0], AbstractGamePiece)
	for cell in cells[1:]: assert cell is None

	cell = Cell(board.last_column, board.last_row)
	board.set_cell(cell, AbstractGamePiece(cell, "r"))
	cells = board.row(cell.row)
	assert isinstance(cells[-1], AbstractGamePiece)
	for cell in cells[:-1]: assert cell is None

	cell = Cell(board.last_column, board.last_row)
	board.set_cell(cell, AbstractGamePiece(cell, "r"))
	cells = board.column(cell.column)
	assert isinstance(cells[-1], AbstractGamePiece)
	for cell in cells[:-1]: assert cell is None


def test_cell_copy():
	game = FakeGame()
	board = game.board
	cell1 = Cell(5, 6)
	cell2 = cell1.copy()
	assert cell2.column == cell1.column
	assert cell2.row == cell1.row

	cell2 = cell1.shifted(1)
	assert cell2.column == cell1.column + 1
	assert cell2.row == cell1.row

	cell2 = cell1.shifted(0, 1)
	assert cell2.column == cell1.column
	assert cell2.row == cell1.row + 1

	cell2 = cell1.shifted(-1)
	assert cell2.column == cell1.column - 1
	assert cell2.row == cell1.row

	cell2 = cell1.shifted(0, -1)
	assert cell2.column == cell1.column
	assert cell2.row == cell1.row - 1

	cell2 = cell1.moved(row=7)
	assert cell2.column == cell1.column
	assert cell2.row == 7

	cell2 = cell1.moved(column=5)
	assert cell2.column == 5
	assert cell2.row == cell1.row


