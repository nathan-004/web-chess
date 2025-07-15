from typing import Optional

from game import Position, WHITE, BLACK

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

class King(Piece):
    def __init__(self, color):
        super().__init__(color)
        self.symbol = '\u2654' if color != WHITE else '\u265A'

    def get_moves(self, pos: Position, board) -> list[Position]:
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

                if self.is_valid_pos(pos, new_pos, board) <= self.VALID_LIMIT:
                    moves.append(new_pos)

        return moves

class Queen(Piece):
    def __init__(self, color):
        super().__init__(color)
        self.symbol = '\u2655' if color != WHITE else '\u265B'

    def get_moves(self, pos: Position, board: list) -> list[Position]:
        super().get_moves(pos, board)
        moves = []

        for incr in Bishop.BISHOP_DIRECTIONS + Rook.ROOK_DIRECTIONS:
            current_x, current_y = pos.x + incr.x, pos.y + incr.y
            valid = self.is_valid_pos(pos, Position(current_x, current_y), board)
            while valid == 0:
                moves.append(Position(current_x, current_y))
                current_x += incr.x
                current_y += incr.y
                valid = self.is_valid_pos(pos, Position(current_x, current_y), board)
            if valid == 1:
                moves.append(Position(current_x, current_y))

        return moves

class Rook(Piece):
    ROOK_DIRECTIONS = [Position(-1, 0), Position(1, 0), Position(0, -1), Position(0, 1)]
    def __init__(self, color):
        super().__init__(color)
        self.symbol = '\u2656' if color != WHITE else '\u265C'

    def get_moves(self, pos: Position, board: list) -> list[Position]:
        super().get_moves(pos, board)
        moves = []

        for incr in self.ROOK_DIRECTIONS:
            current_x, current_y = pos.x + incr.x, pos.y + incr.y
            valid = self.is_valid_pos(pos, Position(current_x, current_y), board)
            while valid == 0:
                moves.append(Position(current_x, current_y))
                current_x += incr.x
                current_y += incr.y
                valid = self.is_valid_pos(pos, Position(current_x, current_y), board)
            if valid == 1:
                moves.append(Position(current_x, current_y))
        
        return list(set(moves))

class Bishop(Piece):
    BISHOP_DIRECTIONS = [Position(1, 1), Position(1, -1), Position(-1, -1), Position(-1, 1)]
    def __init__(self, color):
        super().__init__(color)
        self.symbol = '\u2657' if color != WHITE else '\u265D'

    def get_moves(self, pos: Position, board: list) -> list[Position]:
        super().get_moves(pos, board)
        moves = []

        for incr in self.BISHOP_DIRECTIONS:
            current_x, current_y = pos.x + incr.x, pos.y + incr.y
            valid = self.is_valid_pos(pos, Position(current_x, current_y), board)
            while valid == 0:
                moves.append(Position(current_x, current_y))
                current_x += incr.x
                current_y += incr.y
                valid = self.is_valid_pos(pos, Position(current_x, current_y), board)
            if valid == 1:
                moves.append(Position(current_x, current_y))

        return moves

class Knight(Piece):
    def __init__(self, color):
        super().__init__(color)
        self.symbol = '\u2658' if color != WHITE else '\u265E'

    def get_moves(self, pos: Position, board) -> list[Position]:
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
                    moves.append(new_pos)
        
        return moves

class Pawn(Piece):
    def __init__(self, color):
        super().__init__(color)
        self.symbol = '\u2659' if color != WHITE else '\u265F'
        self.direction = -1 if color == WHITE else 1

    def get_moves(self, pos: Position, board) -> list[Position]:
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
            new_pos = Position(pos.x, pos.y + incr_y)

            valid = self.is_valid_pos(pos, new_pos, board)
            
            if valid == 0:
                moves.append(new_pos)
            if valid == 1 or valid == 4:
                break
        
        for incr_x in range(-1, 2, 2):
            new_pos = Position(pos.x + incr_x, pos.y - 1)
            valid = self.is_valid_pos(pos, new_pos, board)
            if valid == 1:
                moves.append(new_pos)

        return moves