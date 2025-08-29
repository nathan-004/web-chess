from typing import NamedTuple, Optional

from app.utils.constants import CHECKMATE, CHECK, PAT, STALEMATE, NONE

class Position(NamedTuple):
    x:int
    y:int

def string_to_position(position:str) -> Position:
    """Retourne l'objet position si l'entrée est correcte sinon None"""
    if not len(position) == 2:
        return None

    if not(position[0].isalpha() and position[1].isdigit()):
        return None
    
    x = ord(position[0]) - ord('a')
    y = 8 - int(position[1])

    if not(0 <= x < 8) or not(0 <= y < 8):
        return None

    return Position(x, y)

def position_to_string(position: Position) -> str:
    """Convertit un objet Position vers une chaîne en notation algébrique (ex: Position(4, 6) ➜ 'e2')."""
    if not (0 <= position.x <= 7 and 0 <= position.y <= 7):
        raise ValueError("Coordonnées hors échiquier")

    col = chr(position.x + ord('a'))
    row = str(8 - position.y)

    return col + row

class Piece:
    VALID_LIMIT = 1 # Constante définissant le renvoi de `self.is_valid_pos` maximum correspondant à un coup valide

    def __init__(self, color, initial_position: Optional[Position] = None):
        self.color = color
        self.symbol = " "
        self.value = 1
        self.moves = []
        self.initial_position = initial_position
        self.has_moved = False

    def get_moves(self, pos: Position, board) -> list:
        if self.initial_position != pos:
            self.has_moved = True

        return []
    
    def special_moves(self, pos:Position, board) -> list:
        if self.initial_position != pos:
            self.has_moved = True

        return []
    
    def is_valid_pos(self, initial_pos: Position, new_pos: Position, board: list[list]) -> int:
        """
        Regarde si le coups est possible
        Renvoie : 
        - Coups possible:
            - 0 -> tombe sur une case vide
            - 1 -> tombe sur une pièce adverse
        - Coups impossible:
            - 2 -> hors du terrain
            - 3 -> coups identique position initiale
            - 4 -> tombe sur une pièce alliée
        """
        if not (0 <= new_pos.x < 8) or not (0 <= new_pos.y < 8): # Regarde si pièce sort du terrain 
            return 2
        if initial_pos.x == new_pos.x and initial_pos.y == new_pos.y:
            return 3
        
        if board[new_pos.y][new_pos.x] is None: # Regarde si pièce tombe sur une case vide
            return 0
        elif board[new_pos.y][new_pos.x].color != board[initial_pos.y][initial_pos.x].color: # Regarde si pièce tombe sur une pièce d'une couleur différente
            return 1
        
        return 4
    
# Constantes définissant le string représentant chaque couleurs
WHITE = "white"
BLACK = "black"

class Move(NamedTuple):
    piece:Piece
    start_pos:Position
    end_pos:Position

    @property
    def pos(self):
        return self.end_pos

    def __eq__(self, other):
        return (
            isinstance(other, Move) and
            self.piece == other.piece and
            self.start_pos == other.start_pos and
            self.end_pos == other.end_pos
        )

    def __hash__(self):
        return hash((self.piece, self.start_pos, self.end_pos))

class SpecialMove(Move):
    """Stocke les coups spéciaux, avec le coups et la représentation qui doit apparaître à l'échiquier"""
    
class Roque(SpecialMove):
    """Stocke les coups du roi et de la tour et le coup devant apparaître à l'échiquier"""
    def __init__(self, king_move:Move, rook_move:Move, direction:Optional[int] = None):
        self.king_move = king_move
        self.rook_move = rook_move
        
        # Calculer la position devant apparaître sur l'échiquier
        if direction is None:
            direction = -1 if rook_move.start_pos.x == 0 else 1
        self.move = Position(king_move.start_pos.x + 2 * direction, king_move.start_pos.y)

    @property
    def pos(self):
        return self.move
    
class Promotion(SpecialMove):
    """Stocke le pion qui contient la promotion"""

    def __new__(cls, piece, start_pos, end_pos, new_piece_type):
        obj = super().__new__(cls, piece, start_pos, end_pos)
        obj.new_piece = new_piece_type
        return obj

    @property
    def pos(self):
        return self.end_pos

    def modify_piece(self, piece_type:Optional[Piece]):
        self.new_piece = piece_type
    
    def __deepcopy__(self, memo):
        from copy import deepcopy
        
        return Promotion(
            deepcopy(self.piece, memo),
            deepcopy(self.start_pos, memo),
            deepcopy(self.end_pos, memo),
            deepcopy(self.new_piece, memo)
        )
    
class EnPassant(SpecialMove):
    """Stocke le pion qui capture en passant et le pion capturé"""
    def __new__(cls, piece, start_pos:Position, end_pos:Position, captured_pawn:Position):
        obj = super().__new__(cls, piece, start_pos, end_pos)
        obj.captured_pawn = captured_pawn
        return obj

    @property
    def pos(self):
        return self.end_pos

    def __deepcopy__(self, memo):
        from copy import deepcopy

        return EnPassant(
            deepcopy(self.piece, memo),
            deepcopy(self.start_pos, memo),
            deepcopy(self.end_pos, memo),
            deepcopy(self.captured_pawn, memo)
        )
# ---------------------------------------------------------------------------
# états de partie
# ---------------------------------------------------------------------------

class Win(str):
    def __new__(cls, color, message):
        obj = str.__new__(cls, message)
        obj.color = color
        return obj

class CheckMate(Win):
    def __new__(cls, color):
        message = f"{CHECKMATE} {color}"
        return super().__new__(cls, color, message)
    
class Stalemate(str):
    def __new__(cls, message = STALEMATE):
        obj = str.__new__(cls, message)
        return obj
    
class Pat(Stalemate):
    def __new__(cls, color):
        message = f"{PAT} {color}"
        return super().__new__(cls, message)
    
class State(str):
    def __new__(cls, color:Optional[str]=None, message=NONE):
        obj = str.__new__(cls, message)
        if color:
            obj.color = color
        return obj

class Normal(State):
    def __new__(cls, color:Optional[str] = None):
        message = f"{NONE} {color}" if color is not None else NONE
        return super().__new__(cls, color, message)

class Check(State):
    def __new__(cls, color):
        message = f'{CHECK} {color}'
        return super().__new__(cls, color, message)