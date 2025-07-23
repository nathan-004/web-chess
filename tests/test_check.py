from app.engine.game import *

def test_is_check_detection():
    # Plateau vide
    b = blank_board()
    # Place un roi blanc
    b[4][4] = King(WHITE, Position(4, 4))
    # Place une reine noire menaçante
    b[4][0] = Queen(BLACK, Position(0, 4))
    board = ChessBoard(b)
    assert board.is_check(WHITE) == True

    # Place un pion blanc pour bloquer la reine
    b[4][2] = Pawn(WHITE, Position(2, 4))
    board = ChessBoard(b)
    assert board.is_check(WHITE) == False

    # Place un roi noir non menacé
    b[0][0] = King(BLACK, Position(0, 0))
    board = ChessBoard(b)
    assert board.is_check(BLACK) == False

def test_checkmate_detection():
    b = blank_board()
    b[0][0] = King(WHITE, Position(0, 0))
    # Place deux tours noires pour le mat
    b[0][2] = Rook(BLACK, Position(2, 0))
    b[1][2] = Rook(BLACK, Position(2, 1))
    board = ConsoleChessboard(b)
    board.display()
    assert board.is_check(WHITE) == True
    assert board.is_checkmate(WHITE, b) == True

    # Echec et mat avec une pièce pouvant s'interposer
    b[7][1] = Rook(WHITE, Position(1, 7))
    board = ConsoleChessboard(b)
    board.display()
    assert board.is_check(WHITE) == True
    assert board.is_checkmate(WHITE, b) == False

    # Place une pièce blanche pour bloquer le mat
    b[1][1] = Pawn(WHITE, Position(1, 1))
    board = ConsoleChessboard(b)
    board.display()
    assert board.is_check(WHITE) == True
    assert board.is_checkmate(WHITE, b) == False

    # Roi noir non menacé
    b = blank_board()
    b[7][7] = King(BLACK, Position(7, 7))
    board = ConsoleChessboard(b)
    board.display()
    assert board.is_check(BLACK) == False
    assert board.is_checkmate(BLACK, b) == False

def test_stalemate_simple_position():
    board = ChessBoard(blank_board())
    
    board.board[7][7] = King(WHITE, Position(7, 7))
    board.board[6][5] = King(BLACK, Position(5, 6))
    board.board[5][6] = Queen(BLACK, Position(6, 5))

    assert board.is_stalemate(color=WHITE) is True

def test_not_stalemate_black_has_move():
    board = ChessBoard(blank_board())

    board.board[7][7] = King(BLACK, Position(7, 7))
    board.board[5][5] = King(WHITE, Position(5, 5))
    board.board[5][6] = Queen(WHITE, Position(6, 5)) 

    ConsoleChessboard(board.board).display()
    assert board.is_stalemate(color=WHITE) is False