from app.engine.game import *
from app.engine.utils import Move

def test_king_moves():
    b = blank_board()
    b[3][3] = King(WHITE)
    moves = b[3][3].get_moves(Position(3,3), b)
    assert len(moves) == 8

    board = ChessBoard()
    moves = board.board[0][4].get_moves(Position(4,0), board.board)
    assert len(moves) == 0

    board.board[0][3] = Pawn(WHITE)
    moves = board.board[0][4].get_moves(Position(4,0), board.board)
    assert len(moves) == 1

def test_knight_moves():
    b = blank_board()
    b[4][4] = Knight(WHITE)
    moves = b[4][4].get_moves(Position(4, 4), b)

    expected = {
        Position(2, 3), Position(2, 5),
        Position(3, 2), Position(3, 6),
        Position(5, 2), Position(5, 6),
        Position(6, 3), Position(6, 5)
    }

    actual_positions = {move.end_pos for move in moves}

    assert actual_positions == expected
    assert len(moves) == 8

def test_pawn_moves():
    # Pion blanc en position initiale, peut avancer de 1 ou 2 cases
    b = blank_board()
    b[6][4] = Pawn(WHITE)
    moves = b[6][4].get_moves(Position(4, 6), b)
    positions = {move.end_pos for move in moves}
    assert Position(4, 5) in positions
    assert Position(4, 4) in positions
    assert len(moves) == 2

    # Pion blanc qui ne peut avancer que d'une case
    b = blank_board()
    b[5][3] = Pawn(WHITE)
    b[5][3].initial_position = Position(3, 7)
    moves = b[5][3].get_moves(Position(3, 5), b)
    positions = [move.end_pos for move in moves]
    assert positions == [Position(3, 4)]

    # Pion blanc qui peut capturer à gauche et à droite
    b = blank_board()
    b[4][2] = Pawn(WHITE)
    b[4][2].initial_position = Position(6, 2)
    b[3][1] = Pawn(BLACK)  # pièce à capturer à gauche
    b[3][3] = Pawn(BLACK)  # pièce à capturer à droite
    moves = b[4][2].get_moves(Position(2, 4), b)
    positions = {move.end_pos for move in moves}
    assert Position(2, 3) in positions  # avance tout droit
    assert Position(1, 3) in positions  # capture à gauche
    assert Position(3, 3) in positions  # capture à droite
    assert len(moves) == 3