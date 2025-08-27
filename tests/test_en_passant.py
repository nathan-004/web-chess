from app.engine.board import ConsoleChessboard, blank_board
from app.engine.utils import Position, Move, EnPassant, string_to_position
from app.engine.pieces import Pawn, Piece, WHITE, BLACK

def test_en_passant_white():
    board = ConsoleChessboard(blank_board())

    w_pawn_start = string_to_position("e4")
    b_pawn_start = string_to_position("f7")
    w_pawn_end = string_to_position("e5")
    b_pawn_end = string_to_position("f5")

    board.board[w_pawn_start.y][w_pawn_start.x] = Pawn(WHITE, string_to_position("e2"))  # e4
    board.board[b_pawn_start.y][b_pawn_start.x] = Pawn(BLACK, b_pawn_start)  # f7

    board.display()
    board.move(Move(board.board[w_pawn_start.y][w_pawn_start.x], w_pawn_start, w_pawn_end))  # e5 to e4
    board.display(board.board)
    board.move(Move(board.board[b_pawn_start.y][b_pawn_start.x], b_pawn_start, b_pawn_end))  # f7 to f5
    
    board.display(board.board)
    print(board.get_moves(w_pawn_end))
    assert any(isinstance(move, EnPassant) for move in board.get_moves(w_pawn_end))
    assert board.get_moves(w_pawn_end) != []