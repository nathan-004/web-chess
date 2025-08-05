from typing import NamedTuple

from app.engine.board import ChessBoard
from app.engine.utils import WHITE, BLACK, Win, Check
from app.utils.constants import CHECKMATE, CHECK, NONE, PAT, STALEMATE

BLACK_ADVANTAGE = -1
WHITE_ADVANTAGE = 1

class Coefficients(NamedTuple):
    """
    Correspond aux coefficients de chaque fonction dans la moyenne des scores
    """
    material: float = 4.0
    control: float = 1.0
    state: float = 2.0
    threat:float = 3.0

def evaluation(black_eval: float, white_eval: float) -> float:
    """
    Décorateur permettant de calculer le score entre black_eval et white_eval en fonction du résultat brut d'une fonction d'évaluation.

    Parameters
    ----------
    black_eval: float
        Valeur de retour maximale si les noirs dominent complètement.
    white_eval: float
        Valeur de retour maximale si les blancs dominent complètement.
    """
    def decorator(function):
        def eval(*args, **kwargs):  # Arguments de la fonction d'évaluation
            score = function(*args, **kwargs)

            assert black_eval != white_eval, "black_eval et white_eval doivent être différents." # Prévient la division par 0

            # Normalisation du score dans l'intervalle [BLACK_ADVANTAGE, WHITE_ADVANTAGE]
            normalized_score = ((score - black_eval) / (white_eval - black_eval)) * (WHITE_ADVANTAGE - BLACK_ADVANTAGE) + BLACK_ADVANTAGE

            normalized_score = max(min(normalized_score, WHITE_ADVANTAGE), BLACK_ADVANTAGE)
            return normalized_score

        return eval
    return decorator

@evaluation(black_eval=0.30, white_eval=0.70)
def evaluation_materielle(board:ChessBoard):
    """Retourne le rapport des valeurs de pièces blanches et des noirs"""
    white = board.get_material_value(WHITE)
    black = board.get_material_value(BLACK)
    total = white + black

    return white/total if total != 0 else 0.5

@evaluation(black_eval=0, white_eval=1)
def control_evaluation(board:ChessBoard):
    """Regarde le nombre de cases controlées par les deux côtés puis retourne le nombre"""
    white = board.get_total_moves_score(WHITE)
    black = board.get_total_moves_score(BLACK)
    total = white + black
    return white/total if total != 0 else 0.5

@evaluation(black_eval=-1, white_eval=1)
def state_evaluation(board:ChessBoard):
    """Retourne un score dépendant de si l'échiquier est en situation d'échecs, d'échecs et mats, ..."""
    state = board.get_state()

    if isinstance(state, Win):
        return 1 if state.color == WHITE else -1
    elif isinstance(state, Check):
        return 0.5 if state.color == WHITE else -0.5
    else:
        return 0
    
@evaluation(black_eval=1, white_eval=0)
def threat_evaluation(board:ChessBoard):
    """Retourne un score correspondant à la valeur des pièces attaquées"""
    white = board.threat_score(WHITE)
    black = board.threat_score(BLACK)
    total = black + white

    return white/total if total != 0 else 0.5
    
def final_evaluation(board:ChessBoard, coeffs:Coefficients):
    """Fais la moyenne des évaluations en utilisant les coefficients"""
    total = 0
    final_score = 0

    for fn, coeff in zip([evaluation_materielle, control_evaluation, state_evaluation, threat_evaluation], coeffs):
        score = fn(board)
        final_score += score * coeff
        total += coeff

    return final_score / total if total != 0 else 0