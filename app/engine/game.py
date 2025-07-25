# ----------------------------------------------
# Logique de jeu                               |
# ----------------------------------------------

from app.engine.board import ChessBoard, board_to_fen
from app.engine.utils import WHITE, BLACK
from app.engine.utils import Move, Position, string_to_position, position_to_string

class Game:
    """Logiques de jeu -> Gestion des coups, tours, échec et mats"""
    turn = WHITE
    players = {WHITE: None, BLACK: None}

    def __init__(self):
        self.chessboard = ChessBoard()

    def join(self, player_username:str, color:str = None) -> int:
        """
        Permet à un joueur de rejoindre la partie en sélectionnant la couleur
        
        Returns
        -------
        bool : True si le joueur a rejoint la partie, False sinon.
        """
        if any([player_username == player for player in self.players.values()]):
            return True
        if all(self.players.values()): # Vérifie qu'il reste des couleurs libres
            return False

        if color is not None and color in self.players:
            if self.players[color] is None:
                self.players[color] = player_username
                return True
        
        for color in self.players:
            if self.players[color] is None:
                self.players[color] = player_username
                return True
        
    def leave(self, player_username:str) -> bool:
        """
        Permet à un joueur de quitter la partie
        
        Returns
        -------
        bool : True si le joueur a quitté la partie, False sinon.
        """
        for color in self.players:
            if self.players[color] == player_username:
                self.players[color] = None
                return True
        return False
    
    def move(self, player_username:str, move:str) -> bool:
        """
        Permet à un joueur de jouer un coup
        
        Returns
        -------
        bool : True si le coup a été joué, False sinon.
        """
        if self.players[self.turn] != player_username:
            return False
        
        if self.chessboard.move(string_to_position(move), self.turn) == 1:
            return False
        self.turn = WHITE if self.turn == BLACK else BLACK
        return True
    
    def get_moves(self, source:str, player_username:str) -> list[str]:
        """
        Retourne les coups possibles pour le joueur
        
        Returns
        -------
        list[str] : Liste des coups possibles sous forme de chaîne de caractères
        """
        if self.players[self.turn] != player_username:
            return []
        
        moves = self.chessboard.get_moves(string_to_position(source))
        return [position_to_string(move.pos) for move in moves]
    
    def get_board(self) -> list[list[str]]:
        """
        Retourne l'échiquier sous forme de liste de listes
        
        Returns
        -------
        list[list[str]] : Échiquier
        """
        return board_to_fen(self.chessboard.board)