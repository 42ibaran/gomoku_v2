import json
from flask import Flask
from flask import jsonify, request, make_response
from algo.constants import BLACK
from algo.maximilian import get_next_move
from algo.move import Move
from flask_cors import CORS
from algo.errors import ForbiddenMoveError
from algo.game import Game

game = None
params = None

app = Flask(__name__)
CORS(app)
app.secret_key = "eui&@!Rkw8GPV55@NvSSdfTWFHyhq1"

session = {}

def message(msg):
    return make_response(jsonify({
        'message' : msg
    }))

@app.route('/')
def home():
    return "", 200

@app.route('/init', methods=["POST"])
def init():
    global app, game, params

    game = Game()
    session['move_lock'] = False

    if app.config['white']:
        game.record_new_move(Move(BLACK, (9, 9)))
    return make_response(jsonify({
        'move': {
            'color': BLACK,
            'position': (9, 9)
        } if app.config['white'] else None,
        'board': game.board.matrix.tolist()
    })), 201

@app.route('/make-move', methods=["POST"])
def make_move():
    global app
    data = request.get_json()

    if game is None:
        return message("Session not found"), 404
    if 'move_lock' in session and session['move_lock'] == True:
        return message("Not your turn"), 400

    session['move_lock'] == True
    print(data['color'], data['position'])
    last_move = Move(data['color'], tuple(data['position']))
    try:
        game.record_new_move(last_move)
    except ForbiddenMoveError:
        session['move_lock'] = False
        return message("Forbiden move"), 400

    maximilian_move = time_maximilian_move = suggestion = time_suggestion = None
    if app.config['maximilian']:
        maximilian_move, time_maximilian_move = get_next_move(game.board)
        game.record_new_move(maximilian_move)
    if app.config['suggestion']:
        suggestion, time_suggestion = get_next_move(game.board)

    response = {
        'move': {
            'color': maximilian_move.color,
            'position': maximilian_move.position
        } if maximilian_move else None,
        'board': game.board.matrix.tolist(),
        'time_move': time_maximilian_move,
        'suggestion': {
            'color': suggestion.color,
            'position': suggestion.position
        } if suggestion else None,
        'time_suggestion': time_suggestion
    }

    return make_response(jsonify(response)), 201

if __name__ == '__main__':
    app.run()
