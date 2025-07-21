from app.engine.pieces import King, Rook, Bishop
from app.engine.utils import Position, Move, SpecialMove
from app.engine.game import blank_board, ChessBoard, ConsoleChessboard
from app.engine.utils import WHITE, BLACK

def find_castling_move(moves, expected_king_pos):
    for move in moves:
        if isinstance(move, SpecialMove) and move.king_move.end_pos == expected_king_pos:
            return move
    return None

def test_white_kingside_castling():
    board = ConsoleChessboard(blank_board())
    board.board[7][4] = King(WHITE, Position(4, 7))
    board.board[7][7] = Rook(WHITE, Position(7, 7))

    moves = board.board[7][4].special_moves(Position(4, 7), board)
    move = find_castling_move(moves, Position(6, 7))
    board.display_moves(4, 7)
    assert move is not None, "Roque côté roi blanc non détecté"
    assert move.king_move.end_pos == Position(6, 7)
    assert move.rook_move.end_pos == Position(5, 7)

def test_white_queenside_castling():
    board = ChessBoard(blank_board())
    board.board[7][4] = King(WHITE, Position(4, 7))
    board.board[7][0] = Rook(WHITE, Position(0, 7))

    moves = board.board[7][4].special_moves(Position(4, 7), board)
    move = find_castling_move(moves, Position(2, 7))

    assert move is not None, "Roque côté dame blanc non détecté"
    assert move.king_move.end_pos == Position(2, 7)
    assert move.rook_move.end_pos == Position(3, 7)


def test_castling_blocked_by_piece():
    board = ChessBoard(blank_board())
    board.board[7][4] = King(WHITE, Position(4, 7))
    board.board[7][7] = Rook(WHITE, Position(7, 7))
    board.board[7][5] = Bishop(WHITE, Position(5, 7))  # Une pièce bloque

    moves = board.board[7][4].special_moves(Position(4, 7), board)
    move = find_castling_move(moves, Position(6, 7))

    assert move is None, "Le roque devrait être interdit si une pièce bloque"

def test_black_kingside_castling():
    board = ChessBoard(blank_board())
    board.board[0][4] = King(BLACK, Position(4, 0))
    board.board[0][7] = Rook(BLACK, Position(7, 0))

    moves = board.board[0][4].special_moves(Position(4, 0), board)
    move = find_castling_move(moves, Position(6, 0))

    assert move is not None, "Roque côté roi noir non détecté"
    assert move.king_move.end_pos == Position(6, 0)
    assert move.rook_move.end_pos == Position(5, 0)

def test_black_kingside_castling_blocked():
    board = ChessBoard(blank_board())
    board.board[0][4] = King(BLACK, Position(4, 0))
    board.board[0][7] = Rook(BLACK, Position(7, 0))
    board.board[0][5] = Bishop(BLACK, Position(0, 0))  # pièce qui bloque le roque

    moves = board.board[0][4].special_moves(Position(4, 0), board)
    move = find_castling_move(moves, Position(6, 0))

    assert move is None, "Roque côté roi noir ne devrait pas être autorisé s'il y a une pièce entre roi et tour"

def test_white_kingside_castling_moved():
    board = ChessBoard(blank_board())
    board.board[7][5] = King(WHITE, Position(4, 7))
    board.board[7][7] = Rook(WHITE, Position(7, 7))

    moves = board.board[7][5].special_moves(Position(5, 7), board)

    assert len(moves) == 0, "Roques trouvés alors que le roi a bougé"

def test_castling_move():
    board = ConsoleChessboard(blank_board())
    board.board[7][4] = King(WHITE, Position(4, 7))
    board.board[7][7] = Rook(WHITE, Position(7, 7))

    moves = board.board[7][4].special_moves(Position(4, 7), board)
    move = moves[0]
    
    board.board = board.get_board(move)
    board.display()