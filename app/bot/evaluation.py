from app.engine.board import ChessBoard
from app.engine.utils import WHITE, BLACK

BLACK_ADVANTAGE = -1
WHITE_ADVANTAGE = 1

def evaluation(black_eval: float, white_eval: float):
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
            print(normalized_score)
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
def threat_evaluation(board:ChessBoard):
    """Regarde le nombre de cases controlées par les deux côtés puis retourne le nombre"""
    white = board.get_total_moves(WHITE)
    black = board.get_total_moves(BLACK)
    total = white + black
    return white/total if total != 0 else 0.5