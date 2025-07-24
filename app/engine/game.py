# ----------------------------------------------
# Logique de jeu                               |
# ----------------------------------------------

from app.engine.board import ChessBoard
from app.engine.utils import WHITE, BLACK
from app.engine.utils import Move, Position, string_to_position

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