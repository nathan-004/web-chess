from flask import Flask, render_template, request, jsonify

from app.engine.game import ChessBoard
from app.engine.utils import string_to_position, position_to_string

app = Flask(__name__)
chessboard = ChessBoard()

@app.route('/')
def home():
    chessboard = ChessBoard()
    return render_template('index.html')

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

    if not source:
        return jsonify({"error": "Source non fournie"}), 400

    start_pos = string_to_position(source)
    if not start_pos:
        return jsonify({"error": "Coordonnée invalide"}), 400

    piece = chessboard.board[start_pos.y][start_pos.x]
    if piece is None:
        return jsonify({"moves": []})

    moves = piece.get_moves(start_pos, chessboard.board)
    moves_str = [position_to_string(pos) for pos in moves]
    print(moves_str)
    return jsonify({"moves": moves_str})


def main():
    app.run(debug=True)
