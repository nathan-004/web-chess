from dataclasses import dataclass
import re

PGN_FILE = "datas/lichess_elite_2025-05.pgn" # Lancement du programme depuis la racine du projet

pattern = r'^(1/2|1|0)-(1/2|1|0)$'

@dataclass
class PgnGame():
    WhiteElo:int = None
    BlackElo:int = None
    Moves:str = None
    Result:str = None

    def is_complete(self) -> bool:
        return all([self.WhiteElo, self.BlackElo, self.Moves, self.Result])

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
                current_game.Moves = current_string

def main():
    count = 0
    for el in get_games():
        count += 1
        print(count)