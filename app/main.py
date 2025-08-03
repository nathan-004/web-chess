from flask import Flask, render_template, request, jsonify, session
from flask import redirect, url_for, flash

from collections import defaultdict
import uuid
import logging

import app.utils.logger_config # Initialise le logger
from app.engine.game import Game
from app.engine.board import board_to_fen
from app.engine.utils import string_to_position, position_to_string, Move
from app.engine.utils import WHITE, BLACK
from app.utils.constants import *

ID_GAME_SIZE = 8
MIN_USERNAME_SIZE = 4

logger = logging.getLogger(app.utils.logger_config.APP_NAME)
app = Flask(__name__)
app.secret_key = '5QuF6Rq9GQ'

# ---------------------------------------------------------------------------
# Création des données
# ---------------------------------------------------------------------------

def create_game_instance():
    game = Game()
    return game

def generate_username_uuid():
    return f"user_{str(uuid.uuid4())[:3]}"

games = defaultdict(create_game_instance)
players = set()

@app.route("/is_valid_username", methods=["POST"])
def is_valid_username():
    data = request.get_json()
    username = data.get("username")

    if len(username) < MIN_USERNAME_SIZE:
        return jsonify({"valid": False, "message": f"Le nom d'utilisateur doit comporter au moins {MIN_USERNAME_SIZE} caractères."})
    if username in players:
        return jsonify({"valid": False, "message": "Nom d'utilisateur déjà utilisé."})
    
    return jsonify({"valid": True})

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
# Messages
# ---------------------------------------------------------------------------

@app.route('/send_message', methods=['POST'])
def add_message():
    data = request.get_json()
    id = data.get("id")
    message = data.get("message")
    username = session.get("player")

    result = games[id].add_message(message, username)

    return jsonify({"valid": result})

@app.route("/get_messages", methods=['POST'])
def get_messages():
    data = request.get_json()
    id = data.get("id")
    reset = data.get("reset")
    username = session.get("player")

    messages = games[id].get_messages(username, reset)

    return jsonify({"messages": messages})

# ---------------------------------------------------------------------------
# Création du jeu                                                    |
# ---------------------------------------------------------------------------

@app.route('/game/<game_id>')
def game_page(game_id):
    if not "player" in session:
        flash(NON_CONNECTE, "error")
        return redirect(url_for("home"))
    current_games = session.get("games", {})
    player = session.get("player")
    logger.warning(games)

    valid_join = games[game_id].join(player)
    
    if not valid_join:
        flash(ERROR_JOIN, "error")
        return redirect(url_for("home"))
    
    orientation = games[game_id].get_orientation(player)
    if game_id not in current_games:
        current_games[game_id] = orientation
        session["games"] = current_games
        session.modified = True
    else:
        orientation = session["games"][game_id]

    games[game_id].join("bot1", None, True)

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
    username = session.get("player")

    moves_str = games[id].get_moves(source, username)

    logger.debug(f"Coups trouvés pour la pièce ({source}) : {moves_str}")
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
    username = session.get("player")

    valid = games[id].move(username, source, dest)
    
    logger.debug(f"Validation du coups : {valid}")
    return jsonify({"valid": valid})

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

    current_state = games[id].get_current_state()
    
    return jsonify(current_state)

@app.route("/get_turn", methods=["POST"])
def get_turn():
    """Retourne la couleur du joueur qui doit jouer"""
    data = request.get_json()
    id = data.get("id")

    return jsonify({"turn": games[id].turn})

def main():
    app.run(host="0.0.0.0", debug=True)