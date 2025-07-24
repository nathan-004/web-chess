from app.engine.board import *

def test_chessboard_creation():
    board = ChessBoard()
    assert board is not None