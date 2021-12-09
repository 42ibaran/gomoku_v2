import json
from flask import Flask
from flask import jsonify, request, make_response
from algo.constants import BLACK
from algo.maximilian import get_next_move
from algo.move import Move #, session
from flask_cors import CORS
from algo.errors import ForbiddenMoveError
from algo.game import Game

import time

game = None
params = None

app = Flask(__name__)
CORS(app, supports_credentials=True)
app.secret_key = "eui&@!Rkw8GPV55@NvSSdfTWFHyhq1"

session = {}

def message(str):
    return make_response(jsonify({
        'message' : str
    }))

def load_params():
    try:
        params = json.load(open("config.json", 'r'))
    except FileNotFoundError as e:
        print("[ERROR]" + e)
        exit()
    return params

@app.route('/')
def home():
    return "", 200

@app.route('/init', methods=["POST"])
def init():
    global game, params

    game = Game()
    session['move_lock'] = False
    params = load_params()
    print(params)
    return message("Session created"), 201

@app.route('/make-move', methods=["POST"])
def make_move():
    data = request.get_json()
    
    if game is None:
        return message("Session not found"), 404
    if 'move_lock' in session and session['move_lock'] == True:
        return message("Not your turn"), 400

    session['move_lock'] == True
    last_move = Move(data['color'], tuple(data['position']))
    try:
        game.record_new_move(last_move)
    except ForbiddenMoveError:
        session['move_lock'] = False
        return message("Forbiden move"), 400

    if params.vs_max:
        last_move, time_maximilian = get_next_move(game.board)
        game.record_new_move(last_move)
    if params.suggestion:
        suggestion_maximilian, time_suggestion = get_next_move(game.board)

    # victhoria_move = victhoria.calculate_move(game.board, move)
    # if victhoria_move == False:
    #     victhoria_move = Move(BLACK, (SIZE - 1, SIZE - 1))
    # if session['vs_ai']:
    #     game.update_board(victhoria_move)
    #     # suggestion = victhoria.calculate_move(game.board, victhoria_move.position, WHITE
    #     response = {
    #         'ai_move' : victhoria_move.position,
    #         'suggestion' : None
    #     }
    # else:
    #     response = {
    #         'ai_move' : None,
    #         'suggestion' : victhoria_move.position
    #     }
    return make_response(jsonify(response)), 201

if __name__ == '__main__':
    app.run()
