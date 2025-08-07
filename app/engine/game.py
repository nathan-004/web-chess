# ----------------------------------------------
# Logique de jeu                               |
# ----------------------------------------------

from typing import Optional, NamedTuple
import time
from collections import defaultdict

from app.utils.constants import CHECKMATE, PAT, STALEMATE
from app.engine.board import ChessBoard, board_to_fen, ConsoleChessboard
from app.engine.utils import WHITE, BLACK
from app.engine.utils import Move, Position, string_to_position, position_to_string

from app.bot.evaluation import evaluation_materielle, control_evaluation, threat_evaluation, final_evaluation, Coefficients
from app.bot.minimax_ab import Node

class Message(NamedTuple):
    sender:str
    content:str

    def to_dict(self) -> dict:
        return {"sender": self.sender, "content": self.content}

class Player(str):
    def __new__(cls, username: str):
        obj = str.__new__(cls, username)
        obj.username = username
        obj.games = {}  # Sous forme {"id partie": "orientation"}
        return obj

    def __eq__(self, value):
        return str(self) == value

    def __str__(self):
        return self.username

    def __repr__(self):
        return f"Player('{self.username}')"

class Bot(Player):
    def __new__(cls, username: str):
        obj = super().__new__(cls, username)
        return obj

    def __eq__(self, value):
        return super().__eq__(value)

    def __repr__(self):
        return f"Bot('{self.username}')"

class Game:
    """Logiques de jeu -> Gestion des coups, tours, échec et mats"""
    END_STATES = set([CHECKMATE, PAT, STALEMATE])

    def __init__(self):
        self.turn = WHITE
        self.players = {WHITE: None, BLACK: None}

        # Temps en secondes
        self.black_time = 600
        self.white_time = 600
        self.start_timer()

        self.chessboard = ChessBoard()

        self.messages = []
        self.messages_received = defaultdict(lambda : 0) # Sous forme {`username`: index}

        self.end = False
        self.processing = False

    def join(self, player_username:str, color:str = None, bot:bool = False) -> bool:
        """
        Permet à un joueur de rejoindre la partie en sélectionnant la couleur
        
        Returns
        -------
        bool : True si le joueur a rejoint la partie, False sinon.
        """
        cs = Bot if bot else Player

        if any([player_username == player for player in self.players.values()]):
            return True
        if all(self.players.values()): # Vérifie qu'il reste des couleurs libres
            return False

        if color is not None and color in self.players:
            if self.players[color] is None:
                self.players[color] = cs(player_username)
                return True
        
        for color in self.players:
            if self.players[color] is None:
                self.players[color] = cs(player_username)
                return True
            
        return False
        
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
    
    def move(self, player_username:str, source:Optional[str] = None, target:Optional[str] = None, move:Optional[Move] = None) -> bool:
        """
        Permet à un joueur de jouer un coup
        
        Returns
        -------
        bool : True si le coup a été joué, False sinon.
        """
        if all([source is None, target is None]) and move is None:
            return False
        if self.end:
            return False

        if self.players[self.turn] != player_username:
            return False
        if move is None:
            move = Move(None, string_to_position(source), string_to_position(target))

        if self.chessboard.move(move) == 1:
            return False
        self.end_timer()
        self.turn = WHITE if self.turn == BLACK else BLACK
        self.start_timer()
        return True
    
    def get_moves(self, source:str, player_username:str) -> list[str]:
        """
        Retourne les coups possibles pour le joueur
        
        Returns
        -------
        list[str] : Liste des coups possibles sous forme de chaîne de caractères
        """
        if self.end:
            return []

        if self.players[self.turn] != player_username:
            return []
        
        try:
            moves = self.chessboard.get_moves(string_to_position(source))
        except Exception as e:
            print(e)
            return []

        return [position_to_string(move.pos) for move in moves]
    
    def get_current_state(self) -> dict:
        """
        Retourne l'état de l'échiquier sous forme de dictionnaire contenant l'échiquier, les joueurs, l'état du jeu
        
        Returns
        -------
        dict : {"board": notation fen, "board_state": échecs, pat, ..., "players": liste des joueurs}
        """
        board_state = self.chessboard.get_state()
        if any([state in self.END_STATES for state in board_state.split(" ")]) or self.no_time_left():
            self.end = True
        elif type(self.players[self.turn]) is Bot:
            if not self.processing:
                self.play_bot()

        return {
            "board": board_to_fen(self.chessboard.board), 
            "board_state": board_state,
            "end": self.end,
            "players": [self.players[WHITE], self.players[BLACK]],
            "black_time": self.get_current_time(BLACK),
            "white_time": self.get_current_time(WHITE),
            "evaluation": self.get_evaluation()
            } 
    
    def get_orientation(self, username:str) -> Optional[str]:
        """Retourne la couleur de l'utilisateur s'il est dans la partie sinon None"""
        for col in self.players:
            if self.players[col] == username:
                return col
            
    def start_timer(self):
        """Stocke le temps présent"""
        self.start_time = time.time()

    def get_current_time(self, color):
        """Retourne la différence du temps stocké avec le temps présent"""  
        if color == self.turn:
            player_time = getattr(self, f"{color}_time") - (time.time() - self.start_time)
        else:
            player_time = getattr(self, f"{color}_time")
        
        return max(player_time, 0)
    
    def end_timer(self):
        """Termine le timer et stocke le temps des joueurs"""
        time = self.get_current_time(self.turn)
        if self.turn == WHITE:
            self.white_time = time
        else:
            self.black_time = time

    def add_message(self, message, username):
        """Ajoute un NamedTuple dans self.messages"""
        message = Message(sender=username, content=message)

        self.messages.append(message)

        return True
    
    def get_messages(self, username:str, reset:bool=False) -> list[dict]:
        """Renvoie les messages que l'utilisateur n'a pas actuellement"""
        messages_size = len(self.messages)
        n_message = self.messages_received[username]
        self.messages_received[username] = messages_size
        if reset:
            return [message.to_dict() for message in self.messages]
        return [message.to_dict() for message in self.messages[n_message:messages_size]]
    
    def no_time_left(self):
        """ Retourne True si un des deux joueurs n'a plus de temps """
        if self.get_current_time(WHITE) <= 0:
            self.end_timer()
            self.end = True
        elif self.get_current_time(BLACK) <= 0:
            self.end_timer
            self.end = True   
        else:
            return False

        return True
    
    def get_evaluation(self):
        """Retourne un nombre entre -1 et 1 correspondant à l'évaluation de la partie"""
        result = final_evaluation(self.chessboard, Coefficients())

        return result
    
    def play_bot(self):
        """Joue un coups si le tours correspond à un bot"""
        if not type(self.players[self.turn]) is Bot:
            return None

        self.processing = True
        root = Node(self.chessboard, None, 1)
        best_move = root.get_best_move()
        print(root.LOG_DEPTH)
        a = self.move(self.players[self.turn], move = best_move.move)
        self.processing = False
        return a
    

class ConsoleGame(Game):
    def __init__(self):
        super().__init__()
        self.chessboard = ConsoleChessboard()

    def play(self):
        """Boucle principale du jeu"""

        while True:
            if not all([player != None for player in self.players.values()]):
                print('Pas suffisament de joueurs')
                break

            self.chessboard.display()

            print(self.players)
            if type(self.players[self.turn]) is Bot:
                move = self.play_bot()
            else:
                move = self.play_player()

    def play_player(self) -> Move:
        """Demande l'input à l'utilisateur puis joue le coups"""
        start_pos = self.get_player_start_pos()
        self.chessboard.display_moves(start_pos.x, start_pos.y)
        end_pos = self.get_player_end_pos(start_pos)

        move = Move(self.chessboard.board[start_pos.y][start_pos.x], start_pos, end_pos)
        result = self.move(self.players[self.turn], move=move)

        return result

    def get_player_start_pos(self) -> Position:
        """Demande la position de départ à l'utilisateur"""
        valid = False

        while not valid:
            valid = input("Pièce à bouger : ")
            valid = self.chessboard.is_valid_start_move(valid, self.turn)
        
        return valid

    def get_player_end_pos(self, start_pos:Position) -> Position:
        """Demande la position de départ à l'utilisateur"""
        valid = False

        while not valid:
            valid = input("Case d'arrivée : ")
            valid = self.chessboard.is_valid_end_move(valid, start_pos)
        
        return valid

def main():
    game = ConsoleGame()
    game.join("User 1")
    game.join("Bot 1", None, bot=True)
    game.play()