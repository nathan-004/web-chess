# ----------------------------------------------------------------------
# Calcule la probabilité de coups à partir des données
#----------------------------------------------------------------------

from typing import Optional

from app.bot.learning.pgn_parser import get_games, StringMove
from app.engine.board import ChessBoard, ConsoleChessboard, board_to_fen
from app.engine.utils import Move, string_to_position, Roque, Promotion
from app.engine.pieces import *
from app.utils.logging import Logger

class Node:
    """Coups dans un arbre de probabilités"""
    def __init__(self, board:ChessBoard, parent):
        self.board = board
        self.parent = parent
        self.childs = {}
        self.repetition:int = 1 # Nombre de fois où ce coups a été joué depuis la suite de coups jouées

class Root(Node):
    """Noeuds de départ"""
    def __init__(self, board:ChessBoard = ChessBoard()):
        self.board = board
        self.childs = {}
        self.repetition:int = 1

class Tree:
    def __init__(self, root:Node = Root()):
        self.root = root
        self.boards = {
            # Sous forme de FEN
        }

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
    
    if move == "O-O":
        if board.turn == WHITE:
            y = 7
        else:
            y = 0

        king_move = Move(King, Position(4, y), Position(6, y))
        rook_move = Move(Rook, Position(7, y), Position(5, y))
        return king_move

    if move == "O-O-O":
        if board.turn == WHITE:
            y = 7
        else:
            y = 0

        king_move = Move(King, Position(4, y), Position(2, y))
        rook_move = Move(Rook, Position(0, y), Position(3, y))

        return king_move

    if move[0] in letters_pieces:
        piece = move[0]
        move = move[1:]
    else:
        piece = "P"
    
    move = move.replace("x", "")
    move = move.replace("+", "")
    move = move.replace("#", "")

    if "=" in move:
        Pawn.NEW_PIECE_TYPE = letters_pieces[move[-1]]

    if move[0].islower() and move[1].islower():
        column = ord(move[0]) - ord('a')
        move = move[1:]
        row = None
    elif move[0].isdigit() and move[1].islower():
        row = 8 - int(move[0])
        move = move[1:]
        column = None
    else:
        column = None
        row = None

    end_position = string_to_position(move[:2])
    start_position = board.get_start_position(end_position, letters_pieces[piece], column=column, row=row)
    
    if piece == "P" and start_position is None:
        start_position = board.get_start_position(end_position, column=column, row=row, board=board.board)

    return Move(letters_pieces[piece], start_position, end_position)

def create_probability_tree(game_limit:Optional[int] = float("inf")) -> Tree:
    logger = Logger()
    logger.debug("Création de l'arbre de probabilité...", time_counter=True)
    tree = Tree()
    tree.boards[board_to_fen(tree.root.board.board)] = tree.root
    game_count = 0
    logger.debug("Arbre initialisé")

    for game in get_games():
        current_node = tree.root
        game_count += 1
        logger.error(f"Analyse de la partie {game_count}...", time_counter=True)
        if game_count >= game_limit:
            break
        for move in game.Moves:
            logger.warning("Début de la gestion du coup", time_counter=True)
            logger.info(f"Début transformation du coup", time_counter=True)
            move = string_to_move(move, current_node.board)
            logger.info(f"Coup transformé en {move}", time_counter=False)

            logger.info(f"Application du coup", time_counter=True)
            new_board = current_node.board.clone()
            new_board.move(move)
            logger.info(f"Coup appliqué", time_counter=False)
            #ConsoleChessboard(new_board.board).display()
            fen = board_to_fen(new_board.board) + " " + new_board.turn

            if not fen in tree.boards:
                new_node = Node(new_board, current_node)
                tree.boards[fen] = new_node
            else:
                new_node = tree.boards[fen]

            if move in current_node.childs:
                current_node.childs[move].repetition += 1
                current_node = new_node
            else:
                current_node.childs[move] = new_node
                current_node = new_node
            logger.warning("Coup géré", time_counter=False)
        logger.error(f"Partie {game_count} analysée", time_counter=False)
    
    return tree

def main():
    tree = create_probability_tree(game_limit=50)