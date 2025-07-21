from flask import Flask, render_template, request, jsonify, session
from collections import defaultdict
import uuid
import logging

from app.engine.game import ChessBoard, board_to_fen
from app.engine.utils import string_to_position, position_to_string, Move
from app.engine.utils import WHITE, BLACK

ID_GAME_SIZE = 8

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
app = Flask(__name__)
app.secret_key = '5QuF6Rq9GQ'

# ---------------------------------------------------------------------------
# Création des données
# ---------------------------------------------------------------------------

def create_chessboard_instance():
    board = ChessBoard()
    board.players = 0
    return board

def generate_username_uuid():
    return f"user_{str(uuid.uuid4())[:8]}"

chessboards = defaultdict(create_chessboard_instance)

@app.route("/init_session", methods=["POST"])
def init_session():
    if "player" in session:
        print("Session existante", session)
        return jsonify({"message": "Session initialisée", "player": session["player"]})
    session["player"] = generate_username_uuid()
    session["games"] = session.get("games", {}) # Prévient que les parties crées lors de la création de la page soit effacées
    return jsonify({"message": "Session initialisée", "player": session["player"]})


@app.route("/create_board_id", methods=["POST"])
def create_chessboard():
    id = str(uuid.uuid4())[:ID_GAME_SIZE]
    chessboards[id] = create_chessboard_instance()
    return jsonify({"id": id})

@app.route('/game/<game_id>')
def game_page(game_id):
    games = session.get("games", {})

    if chessboards[game_id].players >= 2:
        return "<p>Trop de joueurs</p>"
    orientation = WHITE if chessboards[game_id].players == 0 else BLACK

    if game_id not in games:
        games[game_id] = orientation
        session["games"] = games
        session.modified = True
        chessboards[game_id].players += 1
    else:
        orientation = session["games"][game_id]

    return render_template('game.html', game_id=game_id, orientation=orientation)


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
    moves_str = [position_to_string(move.end_pos) for move in moves]
    print(moves_str)
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
    print(Move(chessboards[id].board[start_pos.y][start_pos.x], start_pos, end_pos))
    valid = chessboards[id].move(Move(chessboards[id].board[start_pos.y][start_pos.x], start_pos, end_pos))
    print(not valid == 1)
    return jsonify({"valid": not valid == 1})

@app.route("/get_current_board", methods=["POST"])
def get_board():
    """Retourne l'échiquier en notation fen"""
    data = request.get_json()
    id = data.get("id")

    fen = board_to_fen(chessboards[id].board)
    print(fen)
    return jsonify({"board": fen})

def main():
    app.run(host="0.0.0.0", debug=True)