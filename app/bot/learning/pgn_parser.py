from dataclasses import dataclass
from typing import NamedTuple, Optional
import re

PGN_FILE = "datas/lichess_elite_2025-05.pgn" # Lancement du programme depuis la racine du projet

pattern = r'^(1/2|1|0)-(1/2|1|0)$'

@dataclass
class StringMove():
    move:str = None
    piece:Optional[str] = None
    special:Optional[str] = None # Roque, petit-roque, promotion, etc.

    def __eq__(self, value):
        value == self.move

@dataclass
class PgnGame():
    WhiteElo:int = None
    BlackElo:int = None
    Moves:str = None
    Result:str = None

    def is_complete(self) -> bool:
        return all([self.WhiteElo, self.BlackElo, self.Moves, self.Result])

def get_moves(pgn_moves: str) -> list[StringMove]:
    """
    Prend en entrée les coups récupérés en PGN
    Ex : "1. Nf3 Nf6 2. d4 g6 3. c4 Bg7 4. Nc3 O-O 5. Bf4 d5"
    Retourne une liste de StringMove
    """
    moves = []
    
    # On enlève les numéros de coups et résultats (1-0, 0-1, 1/2-1/2)
    tokens = re.sub(r"\d+\.", "", pgn_moves)
    tokens = re.sub(r"(1-0|0-1|1/2-1/2)", "", tokens)
    tokens = tokens.split()

    for token in tokens:
        special = None
        piece = None

        # Roque
        if token == "O-O":
            special = "castle_kingside"
            piece = "k"
        elif token == "O-O-O":
            special = "castle_queenside"
            piece = "k"
        
        # Promotion
        elif "=" in token:
            special = "promotion"
            piece = token.split("=")[1].lower()
        
        # Sinon détection de pièce (majuscule sauf pion)
        else:
            if token[0].isupper() and token[0] in "KQRBN":
                piece = token[0].lower()
            else:
                piece = "p"  # pion

        moves.append(StringMove(move=token, piece=piece, special=special))
    
    return moves

def get_games():
    """
    Fonction generator (seulement lisible une fois) qui renvoie les parties sous forme d'objet `PgnGame`
    """
    current_game = PgnGame()
    current_string = ""

    with open(PGN_FILE, "r") as pgn_content:
        while True:
            line = pgn_content.readline()
            if line == "":
                break
            if line == "\n":
                continue
            line = line[:-1] # Enlever Newline

            if current_game.is_complete():
                yield current_game
                current_game = PgnGame()
                current_string = ""

            if line.startswith("[") and line.endswith("]"):
                content = line[1:-1].split('"')[:-1]

                if hasattr(current_game, content[0].strip()):  
                    setattr(current_game, content[0].strip(), content[1])
            else:
                line = line.split(" ")
                if re.match(pattern, line[-1]):
                    current_game.Result = line[-1]
                    line = line[:-1]
                current_string += " ".join(line)
                current_game.Moves = get_moves(current_string)

def main():
    for game in get_games():
        print(game)