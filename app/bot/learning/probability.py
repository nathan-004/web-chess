# ----------------------------------------------------------------------
# Calcule la probabilité de coups à partir des données
#----------------------------------------------------------------------

from dataclasses import dataclass
from typing import Optional
from random import random

from app.bot.learning.pgn_parser import get_games, StringMove
from app.engine.board import ChessBoard, ConsoleChessboard
from app.engine.utils import Move, SpecialMove, string_to_position
from app.engine.pieces import *

root = None

class Node:
    pass

@dataclass
class ChildContainer:
    move:str
    board:Node
    repetition:int = 1 # Nombre de fois où ce coups a été joué depuis la suite de coups jouées

class Node:
    """Coups dans un arbre de probabilités"""
    def __init__(self, board:ChessBoard, parent:Node):
        self.board = board
        self.parent = parent
        self.childs = {}

class Root(Node):
    """Noeuds de départ"""
    def __init__(self, board:ChessBoard = ChessBoard()):
        self.childs = {}

def string_to_move(string_move:StringMove, board:ChessBoard = ChessBoard()) -> Move:
    """
    Retourne l'objet Move depuis la chaîne de caractères

    Parameters
    ----------
    string_move:StringMove
        Contient le coups en string comme "e4"
    
    Returns
    -------
    Move
        Contient la position de départ et la position d'arrivée
    """
    PIECES = Piece.__subclasses__()
    letters_pieces = {piece("", None).letter.upper(): piece for piece in PIECES}
    move = string_move.move
    
    if move[0] in letters_pieces:
        piece = move[0]
        move = move[1:]
    else:
        piece = "P"
    
    move = move.replace("x", "")
    move = move.replace("+", "")
    move = move.replace("#", "")

    end_position = string_to_position(move[:2])
    start_position = board.get_start_position(end_position, letters_pieces[piece])
    
    return Move(letters_pieces[piece], start_position, end_position)

def create_probability_tree(game_limit:Optional[int] = float("inf")):
    global root
    root = Root()
    game_count = 0
    boards = {
        # Sous forme échiquier fen : Chessboard Object
    }

    for game in get_games():
        current_node = root
        game_count += 1
        print(game_count)
        if game_count >= game_limit:
            break
        for move in game.Moves:
            if move in current_node.childs:
                current_node.childs[move].repetition += 1
                current_node = current_node.childs[move].board
            else:
                current_node.childs[move] = ChildContainer(move, Node(move, current_node))
                current_node = current_node.childs[move].board

def print_tree(node:Node, depth:int = 0):
    """Fonction récursive permettant l'affichage des coups possibles"""
    indent = " " * depth
    if not type(node) is Root:
        print(f"{indent}{node.move} -> {node.parent.childs[node.move].repetition}")

    for child in node.childs.values():
        new_node = child.move
        print_tree(new_node, depth+1)

def sim_game(node:Node, depth:int = 0, current_pgn:str = ""):
    """Simule une partie à partir de l'aléatoire puis retourne le pgn de la partie crée"""
    n = random() # entre 0 et 1
    size = len(node.childs)
    total = 0
    new_node = None

    for child in node.childs.values():
        total += child.repetition
        if size * n < total:
            print(child.move.move)
            current_pgn += f"{depth // 2}. " if depth % 2 == 0 else ""
            current_pgn += f"{child.move.move} "
            new_node = child.board
            break
    else:
        return current_pgn
    
    return sim_game(new_node, depth + 1, current_pgn)

def main():
    create_probability_tree(game_limit=500)
    pgn = sim_game(root)
    board = ConsoleChessboard()
    for move in pgn.split(" "):
        print(move)
        if move == "":
            break
        if move[0].isdigit() and move[1] == ".":
            continue
        
        new_move = string_to_move(StringMove(move), board)
        print(new_move)
        board.move(new_move)

        board.display()
    print(pgn)