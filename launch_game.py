import argparse
import json
from algo.maximilian import get_next_move, start_background_search, end_background_search
from algo.board import save_hashtables
from algo.constants import WHITE, BLACK, COLOR_DICTIONARY
from algo.errors import ForbiddenMoveError
from algo.game import Game
from algo.move import Move
from server import app

def exit_game():
    save_hashtables()
    print("\nGood bye!")
    exit(0)

def game_over():
    print("Game over.")
    exit_game()

def get_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("-t", "--terminal", action='store_true', help="Play on the terminal.")
    parser.add_argument("-m", "--maximilian", action='store_true', help="Play against Maximilian.")
    parser.add_argument("-s", "--suggestion", action='store_true', help="Receive Maximilian' suggestions.")
    parser.add_argument("-w", "--white", action='store_true', help="Play as white (2nd turn).")
    arguments = parser.parse_args()
    if arguments.white and not arguments.maximilian:
        parser.error("Option -w requires option -m.")
    return arguments

def get_and_record_human_move(game: Game, last_move: Move, is_bg_process: bool):
    move_color = last_move.opposite_color if last_move else BLACK
    bg_process, event, queue = start_background_search(game.board) if is_bg_process else (None, None, None)
    while True:
        try:
            move_position = input("Where would you like to play? <pos_y pos_x> : ")
            human_move = Move(move_color, move_position)
            board = end_background_search(bg_process, event, queue)
            if board is not None:
                game.board = board
            game.record_new_move(human_move)
            break
        except (ForbiddenMoveError, ValueError) as e:
            print(e)
        except KeyboardInterrupt:
            end_background_search(bg_process, event, queue)
            exit_game()
    return human_move

def print_turn(turn, human_turn, last_move):
    print("\n================== [{}][{}]s TURN {:02d} ==================\n".format(
            COLOR_DICTIONARY[last_move.opposite_color if last_move else BLACK],
            "HUMAN" if human_turn else "MAXIM", turn))

def print_maximilian_move(position, time, is_suggestion):
    move_type = "suggestion" if is_suggestion else "move"
    print("Maximilian's {}: {}\nTime: {:.3f}\n".format(move_type, position, time))

def play_in_terminal(params):
    last_move = None
    game = Game()
    human_turn = not params.white
    turn = 1
    game.board.dump()
    while True:
        print_turn(turn, human_turn, last_move)
        if not human_turn:
            last_move, time_maximilian = get_next_move(game.board)
            print_maximilian_move(last_move.position, time_maximilian, False)
            game.record_new_move(last_move)
            human_turn = True
        else:
            if params.suggestion:
                suggestion_maximilian, time_maximilian = get_next_move(game.board)
                print_maximilian_move(suggestion_maximilian.position, time_maximilian, True)
            last_move = get_and_record_human_move(game, last_move, params.suggestion or params.maximilian)
            human_turn = False if params.maximilian else True
        game.dump()
        turn += 1 if last_move.color == WHITE else 0
        if game.is_over:
            return game_over()

if __name__ == "__main__":
    params = get_arguments()
    print("\nWillkoooommen, bienvenuuuue, weeelcooomeeee\nIm Gomokuuuu, au Gomokuuuu, to Gomokuuuuuuuu 💃\n")
    if (params.terminal):
        try:
            play_in_terminal(params)
        except KeyboardInterrupt:
            exit_game()
    else:
        app.config['maximilian'] = params.maximilian
        app.config['suggestion'] = params.suggestion
        app.config['white'] = params.white
        app.run()
