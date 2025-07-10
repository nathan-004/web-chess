from typing import Optional, NamedTuple

# Constantes définissant le string représentant chaque couleurs
WHITE = "white"
BLACK = "black"

class Position(NamedTuple):
    x:int
    y:int

def blank_board() -> list[list]:
    """Retourne un échiquier vide"""
    return [[None for _ in range(8)] for _ in range(8)]

def start_board() -> list[list]:
    """Retourne la configuration de départ"""
    board = [[None for _ in range(8)] for _ in range(8)]

    board[0] = [Rook(BLACK), Knight(BLACK), Bishop(BLACK), Queen(BLACK), King(BLACK), Bishop(BLACK), Knight(BLACK), Rook(BLACK)]
    board[1] = [Pawn(BLACK) for _ in range(8)]

    board[-1] = [Rook(WHITE), Knight(WHITE), Bishop(WHITE), Queen(WHITE), King(WHITE), Bishop(WHITE), Knight(WHITE), Rook(WHITE)]
    board[-2] = [Pawn(WHITE) for _ in range(8)]

    return board

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

class Rook(Piece):
    def __init__(self, color):
        super().__init__(color)
        self.symbol = '\u2656' if color != WHITE else '\u265C'

class Bishop(Piece):
    def __init__(self, color):
        super().__init__(color)
        self.symbol = '\u2657' if color != WHITE else '\u265D'

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

        for incr_y in range(-1, -3 if self.initial_position == pos else -2, -1):
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

class ChessBoard:
    """Contient les positions des pièces"""

    def __init__(self, board:Optional[list] = None):
        if board is None:
            self.board = start_board()
        else:
            self.board = board

    def display(self, board:Optional[list] = None) -> None:
        """
        Affiche l'échiquier dans la console

        Parameters
        ----------
        board:list
            Matrice 8x8 représentant l'échiquier, contient des objets `Piece`
            Si non spécifié, utilise `self.board`
        """
        if board is None:
            board = self.board # Passage par récurrence, pas de modifications

        for y, row in enumerate(board):
            # print(f"\n{'-' * 24}")
            print("")
            for x, piece in enumerate(row):
                print(piece.symbol if piece is not None else " ", end=" |")
        
        print("")

    def display_moves(self, x, y, board:Optional[list] = None) -> None:
        """Affiche l'échiquier et les coups possibles pour la pièce à la position (x,y)"""
        if board is None:
            board = self.board # Passage par récurrence, pas de modifications
        
        assert 8 > x >= 0, "La position X donnée n'est pas valide"
        assert 8 > y >= 0, "La position Y donnée n'est pas valide"

        moves = board[y][x].get_moves(Position(x,y), board)

        for y, row in enumerate(board):
            # print(f"\n{'-' * 24}")
            print("")
            for x, piece in enumerate(row):
                if (x,y) not in moves:
                    print(piece.symbol if piece is not None else " ", end=" |")
                else:
                    print("#", end=" |")
        
        print("")

    def move(self, start_pos, end_pos, board:Optional[list[list]] = None) -> Optional[list[list]]:
        """
        Modifie `self.board` si board n'est pas spécifié, sinon retourne l'échiquier avec le coup fait

        Parameters
        ----------
        start_pos:tuple:(x,y)
        end_pos:tuple:(x,y)
        board:list: échiquier, si non spécifié, modification de `self.board`
        """
        if board is None:
            board = self.board # Passage par référence pour faire des modifications

        # Vérifier si le coup est possible
        if self.valid_move(Position(*start_pos), Position(*end_pos), board):
            board[start_pos[1]][start_pos[0]], board[end_pos[1]][end_pos[0]] = None, board[start_pos[1]][start_pos[0]]
        else:
            return 1

        if not board is self.board:
            return board

    def valid_move(self, start_pos: Position, end_pos: Position, board:Optional[list]=None):
        """Vérifie si un coup peut être joué à partir des règles de mouvements dans les classes des pièces"""
        if not (8 > start_pos.x >= 0):
            return False
        if not (8 > start_pos.y >= 0):
            return False

        if not (8 > end_pos.x >= 0):
            return False
        if not (8 > end_pos.y >= 0):
            return False

        if board is None:
            board = self.board # Passage par référence, ne pas faire de modifications

        if board[start_pos.y][start_pos.x] is None:
            return False

        # Vérifier que la pièce tombe sur une pièce vide ou d'une couleur différente
        if board[end_pos.y][end_pos.x] is not None:
            if board[start_pos.y][start_pos.x].color == board[end_pos.y][end_pos.x].color:
                return False
        
        moves = board[start_pos.y][start_pos.x].get_moves(start_pos, board)
        if end_pos in moves:
            return True
        
        return False

if __name__ == "__main__":
    game = ChessBoard()
    game.display()
    game.display_moves(4, 6)
    game.move((4,6), (4,4))
    game.move((4,4), (4,3))
    game.move((4,3), (4,2))
    print("display")
    game.display_moves(4, 2)
    game.display()