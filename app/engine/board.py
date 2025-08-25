from typing import Optional
import copy
import logging

import app.utils.logger_config
from app.engine.pieces import *
from app.engine.utils import Position, Piece, WHITE, BLACK, Move, SpecialMove
from app.engine.utils import CheckMate, Pat, Normal, Check
from app.utils.constants import CHECKMATE, CHECK, NONE, PAT

logger = logging.getLogger(app.utils.logger_config.APP_NAME)

def blank_board() -> list[list]:
    """Retourne un échiquier vide"""
    return [[None for _ in range(8)] for _ in range(8)]

def start_board() -> list[list]:
    """Retourne la configuration de départ"""
    board = [[None for _ in range(8)] for _ in range(8)]

    # Pièces noires (ligne 0)
    board[0] = [
        Rook(BLACK, Position(0, 0)), 
        Knight(BLACK, Position(1, 0)), 
        Bishop(BLACK, Position(2, 0)), 
        Queen(BLACK, Position(3, 0)), 
        King(BLACK, Position(4, 0)), 
        Bishop(BLACK, Position(5, 0)), 
        Knight(BLACK, Position(6, 0)), 
        Rook(BLACK, Position(7, 0))
    ]
    
    # Pions noirs (ligne 1)
    board[1] = [Pawn(BLACK, Position(x, 1)) for x in range(8)]

    # Pièces blanches (ligne 7)
    board[-1] = [
        Rook(WHITE, Position(0, 7)), 
        Knight(WHITE, Position(1, 7)), 
        Bishop(WHITE, Position(2, 7)), 
        Queen(WHITE, Position(3, 7)), 
        King(WHITE, Position(4, 7)), 
        Bishop(WHITE, Position(5, 7)), 
        Knight(WHITE, Position(6, 7)), 
        Rook(WHITE, Position(7, 7))
    ]
    
    # Pions blancs (ligne 6)
    board[-2] = [Pawn(WHITE, Position(x, 6)) for x in range(8)]

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
        self.turn = WHITE

    def move(self, move:Move, board:Optional[list[list]] = None) -> Optional[list[list]]:
        """
        Modifie `self.board` si board n'est pas spécifié, sinon retourne l'échiquier avec le coup fait

        Parameters
        ----------
        start_pos:tuple:(x,y)  
        end_pos:tuple:(x,y)  
        board:list: échiquier, si non spécifié, modification de `self.board`  
        """
        logger.debug(f"Appel de la fonction move avec {move}")
        is_self_board = board is None
        # Vérifier si le coup est possible
        move = self.valid_move(move, board)
        logger.debug(f"Coups trouvé : {move}")
        if isinstance(move, Move):
            logger.debug(f"{move} est une instance de Move")
            board = self.get_board(move, board)
            if is_self_board:
                logger.debug("Ajout du coups à self.moves")
                self.moves.append(move)
                self.turn = BLACK if self.turn == WHITE else WHITE
        else:
            return 1

        if is_self_board:
            logger.debug("Echiquier de la classe remplacé")
            self.board = board

        return board

    def valid_move(self, move:Move, board:Optional[list]=None, turn=True):
        """Vérifie si un coup peut être joué à partir des règles de mouvements dans les classes des pièces"""
        if not (8 > move.start_pos.x >= 0):
            return False
        if not (8 > move.start_pos.y >= 0):
            return False

        if not (8 > move.end_pos.x >= 0):
            return False
        if not (8 > move.end_pos.y >= 0):
            return False
        
        logger.debug(f"Coordonnées correctes : {move}")

        if board is None:
            board = self.board # Passage par référence, ne pas faire de modifications

        if board[move.start_pos.y][move.start_pos.x] is None:
            logger.info("Tentative de bouger une case vide")
            return False
        
        start_piece = board[move.start_pos.y][move.start_pos.x]
        end_piece = board[move.end_pos.y][move.end_pos.x]

        # Vérifier que la pièce tombe sur une pièce vide ou d'une couleur différente
        if end_piece is not None:
            if start_piece.color == end_piece.color:
                logger.info(f"La pièce tente de se déplacer sur une pièce de la même couleur")
                return False
        
        if turn:
            turn = WHITE if len(self.moves) % 2 == 0 else BLACK
            if board[move.start_pos.y][move.start_pos.x].color != turn:
                logger.info("Mauvais tours")
                return False
        
        moves = start_piece.get_moves(move.start_pos, board) + start_piece.special_moves(move.start_pos, self)
        for piece_move in moves:
            if piece_move.pos == move.pos:
                 move = piece_move
                 break
        else:
            logger.info(f"Coups non trouvé dans {moves}")
            return False
        
        new_board = self.get_board(move, board)
        if self.is_check(color=start_piece.color, board=new_board):
            logger.info("Echecs trouvé")
            return False

        return move
    
    def get_attackers(self, pos:Position, board:Optional[list] = None) -> list[Piece]:
        """Retourne les pièces qui attaquent la pièce à la position donnée"""
        logger.debug("Appel de la fonction get_attackers")
        if board is None:
            board = self.board

        piece = board[pos.y][pos.x]

        if piece is None:
            logger.warning("La position donnée ne correspond pas à une pièce")
            return []
        
        attackers = []
        for piece_type in self.PIECES:
            moves = piece_type(piece.color, Position(0, 0)).get_moves(pos, board)
            for move in moves:
                if isinstance(board[move.end_pos.y][move.end_pos.x], piece_type):
                    attackers.append(board[move.end_pos.y][move.end_pos.x])
                    break
        
        return attackers

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
            if len(self.get_attackers(pos_king, board)) > 0:
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
    
    def is_checkmate(self, color:str = None, board: Optional[list[list]] = None) -> bool:
        """Vérifie si le roi de la couleur donnée est échec et mat"""
        if board is None:
            board = copy.deepcopy(self.board)

        if not self.is_check(color, board):
            return False

        # Vérifie que le roi ne peut plus bouger
        for king_pos in self.find_pieces(King, color, board):
            if len(self.get_moves(king_pos, board)) != 0:
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
                            if len(self.get_moves(Position(x, y), board)) > 0:
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

    def get_moves(self, start_pos:Position, board:Optional[list[list[Optional[Piece]]]] = None, turn=True) -> list[Move]:
        """Retourne les coups possibles d'une pièce en vérifiant qu'il n'y ait pas d'échecs ou pas le bon tour"""
        if board is None:
            board = self.board
        
        if board[start_pos.y][start_pos.x] is None:
            return []
        
        piece = board[start_pos.y][start_pos.x]
        moves = []
        for move in piece.get_moves(start_pos, board):
            if isinstance(self.valid_move(move, board, turn), Move):
                moves.append(move)
        
        moves.extend(piece.special_moves(start_pos, self))
        return moves
    
    def get_all_actions(self, board_:Optional[list] = None) -> list[Move]:
        """Retourne tous les coups possibles"""
        if board_ is None:
            board = self.board
        else:
            board = board_
        actions = []

        for piece_type in self.PIECES:
            for piece_pos in self.find_pieces(piece_type, self.turn if board_ is None else None, board):
                actions.extend(self.get_moves(piece_pos, board))

        return actions
    
    def get_start_position(self, end_position:Position, piece:Piece, column:int = None, board:list[list[Optional[Piece]]] = None) -> Position:
        """
        Cherche la position de départ avec la position d'arrivée et la pièce

        Parameters
        ----------
        end_position:Position
        piece:Piece
        column:int
            Colone de la pièce de départ
        """
        if board is None:
            board = self.board

        pieces_pos = self.find_pieces(piece, color=self.turn, board=board)

        if column is not None:
            for p in pieces_pos:
                if p.y != column:
                    pieces_pos.remove(p)

        for p in pieces_pos:
            for move in self.get_moves(p, board):
                if end_position == move.end_pos:
                    return p

    def get_board(self, move:Move, board:Optional[list] = None) -> Optional[list]:
        """Retourne le coup réalisé sans vérification préalable"""
        if board is None:
            board = self.board
        else:
            board = copy.deepcopy(board) # Préviens le passage par référence

        if isinstance(move, SpecialMove):
            if isinstance(move, Roque):
                board = self.get_board(move.king_move, board)
                board = self.get_board(move.rook_move, board)
            return board 
        else:
            board[move.start_pos.y][move.start_pos.x], board[move.end_pos.y][move.end_pos.x] = None, board[move.start_pos.y][move.start_pos.x]
            return board
        
    def is_pat(self, board:Optional[list[list[Optional[Piece]]]] = None, color = None) -> bool:
        """Renvoie True si l'échiquier renvoyé correspond à une situation de pat"""
        if board is None:
            board = self.board
        
        for piece_type in self.PIECES:
            for piece_pos in self.find_pieces(piece_type, color, board):
                if len(self.get_moves(piece_pos, turn=False)) > 0:
                    return False
        
        return True
    
    def get_state(self, board:Optional[list] = None) -> str:
        """Retourne le status de la partie"""
        if board is None:
            board = self.board

        for color in [WHITE, BLACK]:
            other_color = WHITE if color == BLACK else WHITE
            if self.is_check(color):
                if self.is_checkmate(color):
                    return CheckMate(other_color)
                return Check(other_color)
            elif self.is_pat(color=color):
                return Pat(other_color)
        return Normal()
    
    def get_material_value(self, color:Optional[str] = None, board:Optional[list[list[Optional[Piece]]]] = None) -> int:
        """Retourne la valeur des pièces de la couleur spécifiée ou des deux couleurs"""
        if board is None:
            board = self.board # Passage par référence
        total = 0

        for row in board:
            for piece in row:
                if piece is None:
                    continue
                if piece.color == color or color is None:
                    total += piece.value
        
        return total
    
    def get_total_moves_score(self, color:str, board:Optional[list[list[Optional[Piece]]]] = None) -> int:
        """
        Retourne un score correspondant au contrôle exercé sur l'échiquier
        """
        if board is None:
            board = self.board
        score = 0
        
        for piece_type in self.PIECES:
            pieces = self.find_pieces(piece_type, color, board)
            for piece_pos in pieces:
                moves = self.get_moves(piece_pos, board, False)
                for move in moves:
                    target = board[move.pos.y][move.pos.x]
                    if target is None:
                        score += 1
        
        return score
    
    def threat_score(self, color:str, board:Optional[list] = None) -> int:
        """Valeurs des pièces attaquées par la couleur adverse"""
        if board is None:
            board = self.board

        score = 0
        attacker_color = WHITE if color == BLACK else BLACK
        
        for piece_type in self.PIECES:
            pieces = self.find_pieces(piece_type, attacker_color, board)
            for piece_pos in pieces:
                moves = self.get_moves(piece_pos, board, False)
                for move in moves:
                    target = board[move.pos.y][move.pos.x]
                    if target is None:
                        continue
                    elif target.color == color:
                        score += target.value
        return score

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

        moves = self.get_moves(Position(xx, yy), board)

        move_positions = {move.pos for move in moves}

        for y, row in enumerate(board):
            print("")
            for x, piece in enumerate(row):
                if x == xx and y == yy:
                    print(f"\033[31m{piece.symbol}\033[0m", end=" |")
                elif Position(x, y) in move_positions:
                    print("#", end=" |")
                else:
                    print(piece.symbol if piece is not None else " ", end=" |")
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
        current_move = Move(start_piece, start_move, Position(x, y))
        if not current_move in start_piece.get_moves(Position(start_move.x, start_move.y), self.board):
            print("non respect des mouvements des pièces")
            return False

        return Position(x, y)

def main():
    game = ConsoleChessboard()
    print(board_to_fen(game.board))