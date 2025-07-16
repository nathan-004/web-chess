from app.engine.utils import Position, Piece, WHITE, BLACK

class King(Piece):
    def __init__(self, color):
        super().__init__(color)
        self.symbol = '\u2654' if color != WHITE else '\u265A'
        self.letter = "k"

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
        self.letter = "q"

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
        self.letter = "r"

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
        self.letter = "b"

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
        self.letter = "n"

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
        self.letter = "p"
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