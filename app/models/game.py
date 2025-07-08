from typing import Optional

# Constantes définissant le string représentant chaque couleurs
WHITE = "white"
BLACK = "black"

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
    def __init__(self, color):
        self.color = color
        self.symbol = " "
        self.moves = []

    def get_moves(self, posX, posY, board) -> list:
        return []

class King(Piece):
    def __init__(self, color):
        super().__init__(color)
        self.symbol = '\u2654' if color == WHITE else '\u265A'

    def get_moves(self, posX, posY, board) -> list[tuple]:
        """
        Retourne les mouvements possibles de cette pièce sous forme de liste de tuples (x,y)
        ! Ne regarde pas si le coup met en échec !
        posX:int:position x de la pièce
        posY:int:position Y de la pièce
        board:list # Passage par référence : pas de modifications
        """
        moves = []

        for incr_y in range(-1, 2, 1):
            for incr_x in range(-1,2,1):
                if incr_y == 0 and incr_x == 0:
                    continue
                elif not (0 <= posX+incr_x < 8) or not (0 <= posY+incr_y < 8):
                    continue
                else:
                    new_x, new_y = posX + incr_x, posY + incr_y

                    if board[new_y][new_x] is None:
                        moves.append((new_x, new_y))
                        continue
                    
                    # La nouvelle position renvoie à une pièce
                    cur_color = board[posY][posX].color
                    if cur_color != board[new_y][new_x].color:
                        moves.append((new_x, new_y))

        return moves

class Queen(Piece):
    def __init__(self, color):
        super().__init__(color)
        self.symbol = '\u2655' if color == WHITE else '\u265B'

class Rook(Piece):
    def __init__(self, color):
        super().__init__(color)
        self.symbol = '\u2656' if color == WHITE else '\u265C'

class Bishop(Piece):
    def __init__(self, color):
        super().__init__(color)
        self.symbol = '\u2657' if color == WHITE else '\u265D'

class Knight(Piece):
    def __init__(self, color):
        super().__init__(color)
        self.symbol = '\u2658' if color == WHITE else '\u265E'

class Pawn(Piece):
    def __init__(self, color):
        super().__init__(color)
        self.symbol = '\u2659' if color == WHITE else '\u265F'

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

    def display_move(self, x, y, board:Optional[list] = None) -> None:
        """Affiche l'échiquier et les coups possibles pour la pièce à la position (x,y)"""
        if board is None:
            board = self.board # Passage par récurrence, pas de modifications
        
        assert 8 > x >= 0, "La position X donnée n'est pas valide"
        assert 8 > y >= 0, "La position Y donnée n'est pas valide"

        moves = board[y][x].get_moves(x, y, board)

        for y, row in enumerate(board):
            # print(f"\n{'-' * 24}")
            print("")
            for x, piece in enumerate(row):
                if (x,y) not in moves:
                    print(piece.symbol if piece is not None else " ", end=" |")
                else:
                    print("#", end=" |")
        
        print("")

if __name__ == "__main__":
    game = ChessBoard()
    game.display()
    game.display_move(4, 7)