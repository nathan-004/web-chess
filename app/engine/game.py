from typing import Optional
import copy

from app.engine.pieces import *
from app.engine.utils import Position, Piece, WHITE, BLACK, Move

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

def board_to_fen(board:list[list[Optional[Piece]]]) -> str:
    """Retourne la notation fen de l'échiquier"""
    fen = ""

    for y, row in enumerate(board):
        fen_row = "/" if y != 0 else ""
        blank_count = 0
        for x, piece in enumerate(row):
            if piece is None:
                blank_count += 1
                continue
            if blank_count != 0:
                fen_row += str(blank_count)
                blank_count = 0
            fen_row += piece.letter if piece.color == BLACK else piece.letter.upper()
        if blank_count != 0:
            fen_row += str(blank_count)
        fen += fen_row
    return fen

class ChessBoard:
    """Contient les positions des pièces"""
    PIECES = [cls for cls in Piece.__subclasses__()]

    def __init__(self, board:Optional[list] = None):
        if board is None:
            self.board = start_board()
        else:
            self.board = board
        self.moves = [] # Liste de coups joués

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
            if board is self.board:
                self.moves.append(Move(piece = board[end_pos[1]][end_pos[0]], start_pos=start_pos, end_pos=end_pos))
        else:
            return 1

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
        if not end_pos in moves:
            return False
        
        new_board = copy.deepcopy(board)
        new_board[start_pos.y][start_pos.x], new_board[end_pos.y][end_pos.x] = None, new_board[start_pos.y][start_pos.x]
        if self.is_check(color=board[start_pos.y][start_pos.x].color, board=new_board):
            return False
        
        turn = WHITE if len(self.moves) % 2 == 0 else BLACK
        if board[start_pos.y][start_pos.x].color != turn:
            return False

        return True
    
    def is_check(self, color: Optional[str] = None, board: Optional[list[list]] = None):
        """
        Regarde si le roi est en échecs en regardant si les trajectoires des pièces adverses le touchent
        Regarder les mouvements de chaques pièces à la place du roi
        Si une des pièces du même type se trouve dans les trajectoires il y a échec

        Parameters
        ----------
        color:str
            Si défini, ne cherchera que l'échec sur le roi de la couleur donnée
            Sinon cherchera pour les deux rois
        board:list
        """
        if board is None:
            board = self.board # Passage par référence

        kings = self.find_pieces(King, color, board)

        for pos_king in kings:
            cur_king = board[pos_king.y][pos_king.x]
            for piece_type in self.PIECES:
                moves = piece_type(cur_king.color).get_moves(pos_king, board)
                for pos in moves:
                    if isinstance(board[pos.y][pos.x], piece_type):
                        return True
        
        return False

    def find_pieces(self, piece_type: Piece, color: Optional[str] = None, board: Optional[list[list]] = None) -> list[Position]:
        """Retourne une liste des positions des pièces qui remplissent les conditions données"""  
        if board is None:
            board = self.board

        positions = []
        for y, row in enumerate(board):
            for x, piece in enumerate(row):
                if type(piece) is piece_type and (piece.color == color or color is None):
                    positions.append(Position(x, y))
            
        return positions
    
    def is_checkmate(self, color:str, board: Optional[list[list]]) -> bool:
        """Vérifie si le roi de la couleur donnée est échec et mat"""
        if board is None:
            board = copy.deepcopy(self.board)

        if not self.is_check(color, board):
            return False

        # Vérifie que le roi ne peut plus bouger
        for king_pos in self.find_pieces(King, color, board):
            for move in board[king_pos.y][king_pos.x].get_moves(king_pos, board):
                new_board = self.move(king_pos, move, copy.deepcopy(board))
                if new_board == 1: # Coups non valide
                    continue

                if not self.is_check(color, new_board):
                    return False
                
        # Vérifie qu'une pièce ne peut pas s'interposer
        for king_pos in self.find_pieces(King, color, board):
            for distance in range(1, 9): # Regarde toutes les pièces en commençant par les plus proches du roi
                for incr_y in range(-distance, distance+1):
                    for incr_x in range(-distance, distance+1):
                        if abs(incr_x) + abs(incr_y) == distance:
                            x, y = king_pos.x + incr_x, king_pos.y + incr_y
                            if not(0 <= x < 8) or not(0 <= y < 8):
                                continue

                            piece = board[y][x]
                            if piece is None:
                                continue
                            elif piece.color != board[king_pos.y][king_pos.x].color:
                                continue

                            for piece_move in piece.get_moves(Position(x, y), board):
                                new_board = self.move((x, y), (piece_move.x, piece_move.y), copy.deepcopy(board))
                                if type(new_board) is list:
                                    if not self.is_check(piece.color, new_board):
                                        return False
                                    
        return True # Si le roi est en échec, qu'il ne peut pas bouger, qu'aucune pièce ne peut se mettre au travers : echec et mats
    
    def undo(self, n = 1):
        """
        **Enlève le dernier coup joué**
        ---
        n:int Nombre de derniers coups à enlever
        """
        for _ in range(n):
            if len(self.moves) > 0:
                move = self.moves.pop()
                self.board[move.end_pos.y][move.end_pos.x], self.board[move.start_pos.y][move.start_pos.x] = None, self.board[move.end_pos.y][move.end_pos.x]

    def get_moves(self, start_pos:Position, board:Optional[list[list[Optional[Piece]]]] = None) -> list[Position]:
        """Retourne les coups possibles d'une pièce en vérifiant qu'il n'y ait pas d'échecs ou pas le bon tour"""
        if board is None:
            board = self.board
        
        if board[start_pos.y][start_pos.x] is None:
            return []
        
        piece = board[start_pos.y][start_pos.x]
        moves = []
        for move in piece.get_moves(start_pos, board):
            if self.valid_move(start_pos, move, board):
                moves.append(move)
        
        return moves

# ------------------------ Partie dans la console ------------------------
class ConsoleChessboard(ChessBoard):
    def __init__(self, board:Optional[list] = None):
        super().__init__(board)

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

    def display_moves(self, xx, yy, board:Optional[list] = None) -> None:
        """Affiche l'échiquier et les coups possibles pour la pièce à la position (x,y)"""
        if board is None:
            board = self.board # Passage par récurrence, pas de modifications
        
        assert 8 > xx >= 0, "La position X donnée n'est pas valide"
        assert 8 > yy >= 0, "La position Y donnée n'est pas valide"

        moves = board[yy][xx].get_moves(Position(xx,yy), board)

        for y, row in enumerate(board):
            # print(f"\n{'-' * 24}")
            print("")
            for x, piece in enumerate(row):
                if x == xx and y == yy:
                    print(f"\033[31m{piece.symbol}\033[0m", end=" |")
                elif (x,y) not in moves:
                    print(piece.symbol if piece is not None else " ", end=" |")
                else:
                    print("#", end=" |")
        
        print("")

    def play(self):
        """Lance une partie dans la console"""
        turn = WHITE

        while True:
            # Récupérer la pièce de départ
            self.display()
            passs = False
            user_start_move = ""
            turn = [WHITE, BLACK][len(self.moves)%2]

            valid = self.is_valid_start_move(user_start_move, turn)
            while valid is False:
                user_start_move = input("Pièce à bouger : ")
                if user_start_move.startswith("undo"):
                    self.undo()
                    passs = True
                    break
                valid = self.is_valid_start_move(user_start_move, turn)

            if passs:
                continue
            
            user_start_move = valid
            self.display_moves(user_start_move.x, user_start_move.y)

            # Récupérer où déplacer la pièce sélectionnée
            user_end_move = ""
            valid = self.is_valid_end_move(user_end_move, user_start_move)
            while valid is False:
                user_end_move = input("Où placer la pièce : ")
                if user_end_move == "quit" or user_end_move == "q":
                    passs = True
                    break
                valid = self.is_valid_end_move(user_end_move, user_start_move)
            user_end_move = valid

            if passs:
                continue

            # Déplacer la pièce
            self.move(user_start_move, user_end_move)
            self.display()

    def is_valid_start_move(self, user_input: str, color: str) -> Optional[Position]:
        """
        Vérifie si la pièce donnée par l'utilisateur est valide

        Parameters
        ----------
        user_input:string
            Soit deux chiffres correspondant à `xy`
            Ou une lettre et un chiffre correspondant à `xy`
        color:string
            Couleur du joueur pour vérifier si la pièce est bien la sienne

        Returns
        -------
        False -> Coups non valide
        Position(x, y) -> Coups valide
        """
        # Nettoyage de l'entrée
        user_input = user_input.strip().lower()
        print(user_input, len(user_input))
        if len(user_input) != 2:
            print("Taille de l'input trop grande")
            return False

        # Conversion lettre/chiffre en coordonnées
        if user_input[0].isalpha() and user_input[1].isdigit():
            x = ord(user_input[0]) - ord('a')
            y = 8 - int(user_input[1])
        elif user_input[0].isdigit() and user_input[1].isdigit():
            x = int(user_input[0])
            y = int(user_input[1])
        else:
            print("format non respecté")
            return False

        # Vérification des bornes
        if not (0 <= x < 8 and 0 <= y < 8):
            return False

        piece = self.board[y][x]
        if piece is None or piece.color != color:
            print("pas la bonne pièce")
            return False

        return Position(x, y)

    def is_valid_end_move(self, user_input, start_move: Position) -> Optional[Position]: 
        """
        Vérifie si le coup est valide et respecte les mouvements des pièces
        Retourne False si n'est pas valide sinon la position donnée
        """
        # Nettoyage de l'entrée
        user_input = user_input.strip().lower()
        print(user_input, len(user_input))
        if len(user_input) != 2:
            print("Taille de l'input trop grande")
            return False

        # Conversion lettre/chiffre en coordonnées
        if user_input[0].isalpha() and user_input[1].isdigit():
            x = ord(user_input[0]) - ord('a')
            y = 8 - int(user_input[1])
        elif user_input[0].isdigit() and user_input[1].isdigit():
            x = int(user_input[0])
            y = int(user_input[1])
        else:
            print("format non respecté")
            return False

        # Vérification des bornes
        if not (0 <= x < 8 and 0 <= y < 8):
            return False

        start_piece = self.board[start_move.y][start_move.x]
        if not Position(x, y) in start_piece.get_moves(Position(start_move.x, start_move.y), self.board):
            print("non respect des mouvements des pièces")
            return False

        return Position(x, y)

def main():
    game = ConsoleChessboard()
    print(board_to_fen(game.board))