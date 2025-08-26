from app.engine.pieces import Pawn, Queen
from app.engine.board import ChessBoard, ConsoleChessboard, blank_board
from app.engine.utils import Position, Move

def test_pawn_promotion_white():
    board = ChessBoard(blank_board())

    # placer un pion blanc en avant-dernière rangée (7e rangée = y=6 si 0=bas)
    pawn = Pawn("white", None)
    start_pos = Position(0, 1)
    end_pos = Position(0, 0)
    board.board[start_pos.y][start_pos.x] = pawn

    move = Move(pawn, start_pos, end_pos)
    ConsoleChessboard().display(board.board)
    board.move(move)
    ConsoleChessboard().display(board.board)

    # vérifier que le pion est devenu une dame
    piece = board.board[0][0]
    assert isinstance(piece, Queen), f"Expected Queen, got {type(piece)}"

def test_pawn_promotion_black():
    board = ChessBoard(blank_board())
    board.moves = [""] 

    # placer un pion noir en avant-dernière rangée (2e rangée = y=1 si 0=bas)
    pawn = Pawn("black", None)
    start_pos = Position(0, 6)
    end_pos = Position(0, 7)
    board.board[start_pos.y][start_pos.x] = pawn

    move = Move(pawn, start_pos, end_pos)
    ConsoleChessboard().display(board.board)
    print(board.get_moves(start_pos))
    board.move(move)
    ConsoleChessboard().display(board.board)

    # vérifier que le pion est devenu une dame
    piece = board.board[7][0]
    assert isinstance(piece, Queen), f"Expected Queen, got {type(piece)}"
