from typing import NamedTuple, Optional

class Position(NamedTuple):
    x:int
    y:int

class Piece:
    VALID_LIMIT = 1 # Constante définissant le renvoi de `self.is_valid_pos` maximum correspondant à un coup valide

    def __init__(self, color, initial_position: Optional[Position] = None):
        self.color = color
        self.symbol = " "
        self.moves = []
        self.initial_position = initial_position

    def get_moves(self, pos: Position, board) -> list:
        if self.initial_position is None:
            self.initial_position = pos

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