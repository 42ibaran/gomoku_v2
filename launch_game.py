import argparse
import sys
import time
from algo.board import load_hashtables, save_hashtables
from algo.constants import WHITE, BLACK, EMPTY, COLOR_DICTIONARY
from algo.errors import YouAreDumbException
from algo.game import Game
from algo.maximilian import Maximilian
from algo.move import Move

def get_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("-t", "--terminal", action='store_true', help="Use the terminal.")
    parser.add_argument("-m", "--maximilian", action='store_true', help="Play against Maximilian.")
    parser.add_argument("-s", "--suggestion", action='store_true', help="Receive suggestions.")
    parser.add_argument("-w", "--white", action='store_true', help="Play as white (2nd turn).")
    arguments = parser.parse_args()
    human_vs_maximilian = arguments.maximilian
    terminal = arguments.terminal
    suggestion = arguments.suggestion
    if not terminal:
        info = input("Would you like to use the terminal? [yes/y] ")
        terminal = True if info == "y" else False
    if not human_vs_maximilian:
        info = input("Would you like to play against Maximilian? [yes/y] ")
        human_vs_maximilian = True if info == "y" else False
    if not suggestion:
        info = input("Would you like to receive suggestions? [yes/y] ")
        suggestion = True if info == "y" else False
    return terminal, human_vs_maximilian, suggestion, arguments.white if arguments.white else False

def get_human_move(game, last_move=None):
    move_position = input("Where would you like to play? <pos_y pos_x> : ")
    move_color = last_move.opposite_color if last_move else BLACK
    try:
        human_move = Move(move_color, move_position)
        if game.board.matrix[human_move.position] != EMPTY:
            raise YouAreDumbException("The cell is already taken you dum-dum.")
        return human_move
    except YouAreDumbException as e:
        print(e)
        return get_human_move(game, last_move)

def print_maximilian_move(position, time):
    print("Maximilian's move: {}\nTime: {}".format(position, time))

def print_maximilian_suggestion(position):
    print("Suggested move: {}".format(position))

def game_over_bitch():
    print("It's over bitch.")

def play_in_terminal(human_as_white, human_vs_maximilian, suggestion):
    last_move = None
    game = Game()
    maximilian = Maximilian()
    human_turn = False if human_as_white else True
    turn = 0
    while True:
        print("\n=================== [{}][{}]s TURN ===================\n".format(
                "HUMAN" if human_turn else "MAXIM",
                COLOR_DICTIONARY[last_move.opposite_color if last_move else BLACK]))
        if human_vs_maximilian and not human_turn:
            last_move, time_maximilian = maximilian.get_next_move(game.board)
            print_maximilian_move(last_move.position, time_maximilian)
        else:
            if suggestion:
                suggestion_maximilian, _ = maximilian.get_next_move(game.board)
                print_maximilian_suggestion(suggestion_maximilian.position)
            last_move = get_human_move(game, last_move)
        game.record_new_move(last_move)
        game.dump()
        print("TURN: {}".format(turn))
        if game.is_over:
            return game_over_bitch()
        human_turn = not human_turn if human_vs_maximilian else True
        turn += 1 if last_move.color == WHITE else 0

def play_in_web(game, human_vs_maximilian, maximilian):
    print("LOOOOOOOOL")

if __name__ == "__main__":
    terminal, human_vs_maximilian, suggestion, human_as_white = get_arguments()
    play_by_option = {
        True: play_in_terminal,
        False: play_in_web
    }
    try:
        load_hashtables()
        play_by_option[terminal](human_as_white, human_vs_maximilian, suggestion)
    except KeyboardInterrupt:
        pass
    save_hashtables()
    print("\nGood bye!")
