import logging
from typing import Union, Optional

from app.engine.utils import Position, Piece, WHITE, BLACK, Move, Roque, Promotion, EnPassant
import app.utils.logger_config

logger = logging.getLogger(app.utils.logger_config.APP_NAME)

class King(Piece):
    def __init__(self, color: str, initial_position: Position):
        super().__init__(color)
        self.symbol = '\u2654' if color != WHITE else '\u265A'
        self.letter = "k"
        self.value = 0
        self.initial_position = initial_position

    def get_moves(self, pos: Position, board) -> list[Move]:
        """
        Retourne les mouvements possibles de cette pièce sous forme de liste de tuples (x,y)
        ! Ne regarde pas si le coup met en échec !
        posX:int:position x de la pièce
        posY:int:position Y de la pièce
        board:list # Passage par référence : pas de modifications
        """
        super().get_moves(pos, board)
        moves = []

        for incr_y in range(-1, 2, 1):
            for incr_x in range(-1,2,1):
                if incr_y == 0 and incr_x == 0:
                    continue

                new_pos = Position(pos.x + incr_x, pos.y + incr_y)
                logger.debug(f"Objet King : Vérification du move {new_pos} pour {self} en {pos}")
                if self.is_valid_pos(pos, new_pos, board) <= self.VALID_LIMIT:
                    moves.append(Move(self, pos, new_pos))

        return moves
    
    def special_moves(self, pos:Position, board) -> list[Roque]:
        """
        Retourne une liste de coups spéciaux : qui font intervenir plusieurs pièces

        Parameters
        ----------
        pos:Position
        board:ChessBoard
            Objet chessboard

        Returns
        -------
        list[Roque]: Liste de coups possibles
        """
        super().special_moves(pos, board)
        if self.initial_position != pos:
            return []
        
        row = 7 if self.color == WHITE else 0
        moves = []

        def can_castle(x_direction: int) -> bool:
            x = pos.x + x_direction

            while 0 <= x < 8:
                piece = board.board[pos.y][x]
                if piece is not None:
                    if isinstance(piece, Rook) and not piece.has_moved and piece.color == self.color:
                        return True
                    else:
                        return False
                x += x_direction
            return False

        if can_castle(+1):
            king_target = Position(6, pos.y)
            rook_start = Position(7, pos.y)
            rook_target = Position(5, pos.y)

            moves.append(
                Roque(
                    Move(self, pos, king_target),
                    Move(board.board[pos.y][7], rook_start, rook_target),
                    +1
                )
            )

        if can_castle(-1):
            king_target = Position(2, pos.y)
            rook_start = Position(0, pos.y)
            rook_target = Position(3, pos.y)

            moves.append(
                Roque(
                    Move(self, pos, king_target),
                    Move(board.board[pos.y][0], rook_start, rook_target),
                    -1
                )
            )
        
        return moves

class Queen(Piece):
    def __init__(self, color: str, initial_position: Position):
        super().__init__(color)
        self.symbol = '\u2655' if color != WHITE else '\u265B'
        self.letter = "q"
        self.value = 8
        self.initial_position = initial_position

    def get_moves(self, pos: Position, board: list) -> list[Move]:
        super().get_moves(pos, board)
        moves = []

        for incr in Bishop.BISHOP_DIRECTIONS + Rook.ROOK_DIRECTIONS:
            current_x, current_y = pos.x + incr.x, pos.y + incr.y
            valid = self.is_valid_pos(pos, Position(current_x, current_y), board)
            while valid == 0:
                moves.append(Move(self, pos, Position(current_x, current_y)))
                current_x += incr.x
                current_y += incr.y
                valid = self.is_valid_pos(pos, Position(current_x, current_y), board)
            if valid == 1:
                moves.append(Move(self, pos, Position(current_x, current_y)))

        return moves

class Rook(Piece):
    ROOK_DIRECTIONS = [Position(-1, 0), Position(1, 0), Position(0, -1), Position(0, 1)]
    def __init__(self, color: str, initial_position: Position):
        super().__init__(color)
        self.symbol = '\u2656' if color != WHITE else '\u265C'
        self.letter = "r"
        self.value = 5
        self.initial_position = initial_position

    def get_moves(self, pos: Position, board: list) -> list[Move]:
        super().get_moves(pos, board)
        moves = []

        for incr in self.ROOK_DIRECTIONS:
            current_x, current_y = pos.x + incr.x, pos.y + incr.y
            valid = self.is_valid_pos(pos, Position(current_x, current_y), board)
            while valid == 0:
                moves.append(Move(self, pos, Position(current_x, current_y)))
                current_x += incr.x
                current_y += incr.y
                valid = self.is_valid_pos(pos, Position(current_x, current_y), board)
            if valid == 1:
                moves.append(Move(self, pos, Position(current_x, current_y)))
        
        return list(set(moves))

class Bishop(Piece):
    BISHOP_DIRECTIONS = [Position(1, 1), Position(1, -1), Position(-1, -1), Position(-1, 1)]
    def __init__(self, color: str, initial_position: Position):
        super().__init__(color)
        self.symbol = '\u2657' if color != WHITE else '\u265D'
        self.letter = "b"
        self.value = 3
        self.initial_position = initial_position

    def get_moves(self, pos: Position, board: list) -> list[Move]:
        super().get_moves(pos, board)
        moves = []

        for incr in self.BISHOP_DIRECTIONS:
            current_x, current_y = pos.x + incr.x, pos.y + incr.y
            valid = self.is_valid_pos(pos, Position(current_x, current_y), board)
            while valid == 0:
                moves.append(Move(self, pos, Position(current_x, current_y)))
                current_x += incr.x
                current_y += incr.y
                valid = self.is_valid_pos(pos, Position(current_x, current_y), board)
            if valid == 1:
                moves.append(Move(self, pos, Position(current_x, current_y)))

        return moves

class Knight(Piece):
    def __init__(self, color: str, initial_position: Position):
        super().__init__(color)
        self.symbol = '\u2658' if color != WHITE else '\u265E'
        self.letter = "n"
        self.value = 3
        self.initial_position = initial_position

    def get_moves(self, pos: Position, board) -> list[Move]:
        """        
        Retourne les mouvements possibles de cette pièce sous forme de liste de tuples (x,y)  
        ! Ne regarde pas si le coup met en échec !  
        posX:int:position x de la pièce  
        posY:int:position Y de la pièce  
        board:list # Passage par référence : pas de modifications  
        """
        super().get_moves(pos, board)
        moves = []

        for dir in [(-2, 0), (0, 2), (2, 0), (0, -2)]: # Liste des directions possibles (x,y)
            for move in range(-1, 2, 2):
                move_x, move_y = move if dir[0] == 0 else 0, move if dir[1] == 0 else 0 # Regarde sur quel axe regarder des deux côtés
                new_pos = Position(pos.x + dir[0] + move_x, pos.y + dir[1] + move_y)
                
                if self.is_valid_pos(pos, new_pos, board) <= self.VALID_LIMIT:
                    moves.append(Move(self, pos, new_pos))
        
        return moves

class Pawn(Piece):
    NEW_PIECE_TYPE = Queen
    def __init__(self, color: str, initial_position: Position):
        super().__init__(color)
        self.symbol = '\u2659' if color != WHITE else '\u265F'
        self.letter = "p"
        self.value = 1
        self.direction = -1 if color == WHITE else 1
        self.initial_position = initial_position

    def get_moves(self, pos: Position, board) -> list[Move]:
        """        
        Retourne les mouvements possibles de cette pièce sous forme de liste de tuples (x,y)  
        ! Ne regarde pas si le coup met en échec !  
        posX:int:position x de la pièce  
        posY:int:position Y de la pièce  
        board:list # Passage par référence : pas de modifications  
        """
        super().get_moves(pos, board)
        moves = []
        for incr_y in range(1 * self.direction, 3 * self.direction if self.initial_position == pos else 2 * self.direction, 1 * self.direction):
            if not 0 < pos.y + incr_y < 7:
                break
            new_pos = Position(pos.x, pos.y + incr_y)

            valid = self.is_valid_pos(pos, new_pos, board)

            if valid == 0:
                moves.append(Move(self, pos, new_pos))
            if valid == 1 or valid == 4:
                break
        
        for incr_x in range(-1, 2, 2):
            if 0 < pos.y + self.direction < 7:
                new_pos = Position(pos.x + incr_x, pos.y + self.direction)
                valid = self.is_valid_pos(pos, new_pos, board)
                if valid == 1:
                    moves.append(Move(self, pos, new_pos))
        return moves
    
    def get_en_passant(self, pos:Position, board) -> Optional[EnPassant]:
        """Regarde si une prise en passant est possible à une position donnée"""
        moves = []
        if not board.moves:
            return None
        
        last_move = board.moves[-1]
        if not isinstance(last_move.piece, Pawn):
            return None
        
        if abs(last_move.start_pos.y - last_move.end_pos.y) != 2:
            return None
        
        if last_move.end_pos.y != pos.y:
            return None
        
        if abs(last_move.end_pos.x - pos.x) != 1:
            return None
        
        new_pos = Position(last_move.end_pos.x, last_move.end_pos.y + self.direction)
        if self.is_valid_pos(pos, new_pos, board.board) == 0:
            return EnPassant(
                self,
                pos,
                new_pos,
                last_move.end_pos,
            )
        
        return None

    def special_moves(self, pos:Position, board) -> list[Union[Promotion, EnPassant]]:
        """
        Retourne s'il y a un cas de :
        - promotion
        - prise en passant
        """
        super().special_moves(pos, board)
        moves = []

        for incr_x in range(-1, 2, 2):
            if 0 < pos.y + self.direction < 7:
                new_pos = Position(pos.x + incr_x, pos.y + self.direction)
                move = self.get_en_passant(pos, board) 
                if move is not None:
                    moves.append(move)
        if 1 < pos.y < 6:
            return moves

        new_pos = Position(pos.x, pos.y + self.direction)
        valid = self.is_valid_pos(pos, new_pos, board.board)

        if valid == 0:
            moves.append(Promotion(self, pos, new_pos, self.NEW_PIECE_TYPE))

        for incr_x in range(-1, 2, 2):
            new_pos = Position(pos.x + incr_x, pos.y + self.direction)
            valid = self.is_valid_pos(pos, new_pos, board.board)
            if valid == 1:
                moves.append(Promotion(self, pos, new_pos, self.NEW_PIECE_TYPE))
        
        return moves