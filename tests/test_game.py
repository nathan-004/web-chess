from app.models.game import *

def test_chessboard_creation():
    board = ChessBoard()
    assert board is not None

# ------------------- Tests Coups possibles -----------------
def test_king_moves():
    b = blank_board()
    b[3][3] = King(WHITE)
    moves = b[3][3].get_moves(Position(3,3), b)
    assert len(moves) == 8

    board = ChessBoard()
    moves = board.board[0][4].get_moves(Position(4,0), board.board)
    assert len(moves) == 0