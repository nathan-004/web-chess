# ---------------------------------------------------------------------
# Implémentation de l'algorithme Minimax avec optimisation alpha-bêta 
#----------------------------------------------------------------------

from typing import NamedTuple, Optional
from copy import deepcopy
from random import randint

from app.engine.board import ChessBoard
from app.engine.utils import Move, Win, Stalemate, WHITE, BLACK, SpecialMove

from app.bot.evaluation import Coefficients, final_evaluation

class BestMove(NamedTuple):
    move:Move
    value:float

class Node():
    # Contient un coups et l'échiquier
    def __init__(self, board:ChessBoard, move:Move, depth:int):
        """
        Parameters
        ----------
        board:Chessboard
            Echiquier avec le move joué
        move:Move
            Dernier coups joué
        """
        self.board = board
        self.move = move
        self.depth = depth
        self.player = board.turn

    def get_best_move(self, coeffs:Coefficients = Coefficients(), alpha: float = -1.0, beta:float = 1.0) -> BestMove:
        """Retourne le coups réduisant le plus les risques"""
        # Vérifier que la profondeur maximale n'a pas été atteinte
        if self.depth <= 0:
            return BestMove(self.move, self.eval(coeffs))

        # Stoppe ici si la partie est finie
        state = self.board.get_state()
        if isinstance(state, Win):
            return BestMove(self.move, self.eval(coeffs))
        elif isinstance(state, Stalemate):
            return BestMove(self.move, self.eval(coeffs))
        
        best_move = None

        for move in self.board.get_all_actions():
            if isinstance(move, SpecialMove):
                move = move.king_move
            new_board = deepcopy(self.board)
            new_board.move(move)

            value = Node(new_board, move, self.depth - 1).get_best_move(coeffs, alpha, beta)
            best_move = self.best_between_two(best_move, value)

            if self.player == WHITE:
                alpha = max(alpha, best_move.value)
            else:
                beta = min(beta, best_move.value)

            if beta <= alpha:
                break

        return best_move

    def eval(self, coeffs:Coefficients):
        """Retourne un float entre -1 et 1"""
        score = final_evaluation(self.board, coeffs)

        return score
    
    def best_between_two(self, best_move1:Optional[BestMove], best_move2:Optional[BestMove]) -> BestMove:
        """Retourne le meilleur élément parmi les deux entrées"""
        if best_move1 is None:
            return best_move2
        elif best_move2 is None:
            return best_move1
        
        if best_move1.value == best_move2.value:
            return [best_move1, best_move2][randint(0, 1)]

        fn = max if self.player == WHITE else min

        if fn(best_move1.value, best_move2.value) == best_move1.value:
            return best_move1
        else:
            return best_move2