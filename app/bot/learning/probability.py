# ----------------------------------------------------------------------
# Calcule la probabilité de coups à partir des données
#----------------------------------------------------------------------

from dataclasses import dataclass
from typing import Optional
from random import random

from app.bot.learning.pgn_parser import get_games, StringMove

root = None

class Node:
    pass

@dataclass
class ChildContainer:
    move:Node
    repetition:int = 1 # Nombre de fois où ce coups a été joué depuis la suite de coups jouées

class Node:
    """Coups dans un arbre de probabilités"""
    def __init__(self, move:StringMove, parent:Node):
        self.move = move
        self.parent = parent
        self.childs = {}

class Root(Node):
    """Noeuds de départ"""
    def __init__(self):
        self.childs = {}

def create_probability_tree(game_limit:Optional[int] = float("inf")):
    global root
    root = Root()
    game_count = 0

    for game in get_games():
        current_node = root
        game_count += 1
        print(game_count)
        if game_count >= game_limit:
            break
        for move in game.Moves:
            if move in current_node.childs:
                current_node.childs[move].repetition += 1
                current_node = current_node.childs[move].move
            else:
                current_node.childs[move] = ChildContainer(Node(move, current_node))
                current_node = current_node.childs[move].move

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
            new_node = child.move
            break
    else:
        return current_pgn
    
    return sim_game(new_node, depth + 1, current_pgn)

def main():
    create_probability_tree(game_limit=500)
    print(sim_game(root))