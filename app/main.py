from flask import Flask, render_template, request, jsonify, session
from flask import redirect, url_for, flash

from collections import defaultdict
import uuid
import logging

import app.utils.logger_config # Initialise le logger
from app.engine.board import ChessBoard, board_to_fen
from app.engine.utils import string_to_position, position_to_string, Move
from app.engine.utils import WHITE, BLACK
from app.utils.constants import *

ID_GAME_SIZE = 8

logger = logging.getLogger(app.utils.logger_config.APP_NAME)
app = Flask(__name__)
app.secret_key = '5QuF6Rq9GQ'

# ---------------------------------------------------------------------------
# Création des données
# ---------------------------------------------------------------------------

def create_chessboard_instance():
    board = ChessBoard()
    board.players = []
    return board

def generate_username_uuid():
    return f"user_{str(uuid.uuid4())[:8]}"

chessboards = defaultdict(create_chessboard_instance)
players = set()

@app.route("/init_session", methods=["POST"])
def init_session():
    username = request.form["username"]
    player = generate_username_uuid()
    if "player" in session:
        player = session["player"]
    if username:
        if not username in players:
            player = username
            session["games"] = {}
    session["player"] = player
    session["games"] = session.get("games", {}) # Prévient que les parties crées lors de la création de la page soit effacées
    flash(f"Bienvenue {player} !", "success")
    return redirect(url_for("home"))

@app.route("/create_board_id", methods=["POST"])
def create_chessboard():
    if "player" not in session:
        flash(NON_CONNECTE, "error")
        return redirect(url_for("home"))
    board_id = request.form.get("board-id", None)
    if not board_id:
        board_id = str(uuid.uuid4())[:ID_GAME_SIZE]
    return redirect(url_for("game_page", game_id=board_id))

# ---------------------------------------------------------------------------
# Menu
# ---------------------------------------------------------------------------

@app.route("/")
def home():
    return render_template('index.html')

# ---------------------------------------------------------------------------
# Création du jeu                                                    |
# ---------------------------------------------------------------------------

@app.route('/game/<game_id>')
def game_page(game_id):
    if not "player" in session:
        flash(NON_CONNECTE, "error")
        return redirect(url_for("home"))
    games = session.get("games", {})
    player = session.get("player")
    logger.warning(games)

    if len(chessboards[game_id].players) >= 2 and game_id not in games:
        flash(TROP_JOUEURS, "error")
        return redirect(url_for("home"))
    orientation = WHITE if len(chessboards[game_id].players) == 0 else BLACK
    if game_id not in games:
        games[game_id] = orientation
        session["games"] = games
        session.modified = True
        chessboards[game_id].players.append(player)
    else:
        orientation = session["games"][game_id]

    return render_template('game.html', game_id=game_id, orientation=orientation)

# ---------------------------------------------------------------------------
# Logique de jeu
# ---------------------------------------------------------------------------

@app.route('/get_moves', methods=['POST'])
def get_moves():
    """
    Retourne les coups possibles sous forme de notation (e4, f6, etc.)
    ---
    Reçoit : {"source": "e2"}
    Renvoie : {"moves": ["e3", "e4"]}
    """
    data = request.get_json()
    source = data.get('source')
    id = data.get('id')
    orientation = session["games"][id]

    if not source:
        return jsonify({"error": "Source non fournie"}), 400

    start_pos = string_to_position(source)
    if not start_pos:
        return jsonify({"error": "Coordonnée invalide"}), 400

    piece = chessboards[id].board[start_pos.y][start_pos.x]
    if piece is None:
        return jsonify({"moves": []})
    if piece.color != orientation:
        return jsonify({"error": "Pièce de la mauvaise couleur"})

    moves = chessboards[id].get_moves(start_pos)
    moves_str = [position_to_string(move.pos) for move in moves]
    logger.debug(f"Coups trouvés pour la pièce ({start_pos}) : {moves_str}")
    return jsonify({"moves": moves_str})

@app.route('/move', methods=['POST'])
def move_piece():
    """
    Joue un coups sur l'échiquier du serveur
    ---
    Reçoit : {"source": "e2", "destination": "e4"}
    Renvoie : {"valid": True}
    """
    data = request.get_json()
    source = data.get("source")
    dest = data.get("destination")
    id = data.get("id")
    orientation = session["games"][id]

    if not source or not dest:
        return jsonify({"error": "Position non fournies"}), 400
    
    start_pos, end_pos = string_to_position(source), string_to_position(dest)
    if not start_pos or not end_pos:
        return jsonify({"error": "Coordonnée invalide"}), 400
    
    if chessboards[id].board[start_pos.y][start_pos.x].color != orientation:
        return jsonify({"error": "Pas la bonne pièce à jouer"}), 400
    valid = chessboards[id].move(Move(chessboards[id].board[start_pos.y][start_pos.x], start_pos, end_pos))
    logger.debug(f"Validation du coups : {not valid == 1}")
    return jsonify({"valid": not valid == 1})

@app.route("/get_current_board", methods=["POST"])
def get_board():
    """
    Retourne
    --------
    `board`: str
        échiquier sous forme de notation FEN
    `board_state`: string
        Retourne l'état de l'échiquier -> echec, echec et mats, pat, none
    """
    data = request.get_json()
    id = data.get("id")

    fen = board_to_fen(chessboards[id].board)
    state = chessboards[id].get_state()
    players = chessboards[id].players
    
    return jsonify({"board": fen, "board_state": state, "players": players})

@app.route("/get_turn", methods=["POST"])
def get_turn():
    """Retourne la couleur du joueur qui doit jouer"""
    data = request.get_json()
    id = data.get("id")

    return jsonify({"turn": WHITE if len(chessboards[id].moves) % 2 == 0 else BLACK})

def main():
    app.run(host="0.0.0.0", debug=True)