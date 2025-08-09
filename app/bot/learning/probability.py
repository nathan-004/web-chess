# ----------------------------------------------------------------------
# Calcule la probabilité de coups à partir des données
#----------------------------------------------------------------------

from dataclasses import dataclass
from typing import Optional

from app.bot.learning.pgn_parser import get_games, StringMove

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
    
    #print_tree(root)

def print_tree(node:Node, depth:int = 0):
    """Fonction récursive permettant l'affichage des coups possibles"""
    indent = " " * depth
    if not type(node) is Root:
        print(f"{indent}{node.move} -> {node.parent.childs[node.move].repetition}")

    for child in node.childs.values():
        new_node = child.move
        print_tree(new_node, depth+1)

def main():
    create_probability_tree()
