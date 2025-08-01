import pytest
from app.engine.board import ChessBoard
from app.engine.utils import WHITE, BLACK
from app.engine.pieces import Rook, Queen, Pawn, King
from app.engine.utils import Position
from app.bot.evaluation import evaluation_materielle

def test_material_eval_start():
    board = ChessBoard()
    assert evaluation_materielle(board) == pytest.approx(0.0, abs=1e-6), "Égalité au départ doit retourner 0.0"

def test_empty_board():
    board = ChessBoard()
    board.board = [[None for _ in range(8)] for _ in range(8)]
    assert evaluation_materielle(board) == 0.0, "Plateau vide = égalité (0.0)"

def test_white_advantage():
    board = ChessBoard()
    board.board = [[None for _ in range(8)] for _ in range(8)]
    board.board[0][0] = Queen(WHITE, Position(0, 0))
    board.board[0][1] = Pawn(WHITE, Position(0, 1))
    assert evaluation_materielle(board) > 0.0, "Blancs avantagés -> score > 0"

def test_black_advantage():
    board = ChessBoard()
    board.board = [[None for _ in range(8)] for _ in range(8)]
    board.board[7][7] = Rook(BLACK, Position(7, 7))
    board.board[6][7] = Pawn(BLACK, Position(6, 7))
    assert evaluation_materielle(board) < 0.0, "Noirs avantagés -> score < 0"

def test_only_kings():
    board = ChessBoard()
    board.board = [[None for _ in range(8)] for _ in range(8)]
    board.board[0][0] = King(WHITE, Position(0, 0))
    board.board[7][7] = King(BLACK, Position(7, 7))
    assert evaluation_materielle(board) == 0.0, "Rois seuls = égalité"
