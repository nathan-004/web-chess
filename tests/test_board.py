from app.models.game import *

def test_chessboard_creation():
    board = ChessBoard()
    assert board is not None