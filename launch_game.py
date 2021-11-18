import argparse
import sys
import time
from algo.board import load_hashtables, save_hashtables
from algo.constants import WHITE, BLACK
from algo.errors import YouAreDumbException
from algo.game import Game
from algo.maximilian import Maximilian
from algo.move import Move

def get_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("-t", "--terminal", action='store_true', help="Use the terminal")
    parser.add_argument("-m", "--maximilian", action='store_true', help="Play against Maximilian")
    parser.add_argument("-s", "--suggestion", action='store_true', help="Receive suggestions")
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
    return terminal, human_vs_maximilian, suggestion

def get_human_move(game, last_move=None, ):
    move_position = input("Where would you like to play? <pos_y pos_x> : ")
    move_color = last_move.opposite_color if last_move else BLACK
    try:
        human_move = Move(move_color, move_position)
        game.record_new_move(human_move)
        return human_move
    except YouAreDumbException as e:
        print(e)
        return get_human_move(game, last_move)

def game_over_bitch():
    print("It's over bitch.")

def play_in_terminal(game, human_vs_maximilian, suggestion):
    last_move = None
    maximilian = Maximilian()
    while True:
        print("\n=================== HUMAN[BLACK]s TURN ===================\n")
        if suggestion and last_move:
            move_maximilian, _ = maximilian.get_next_move(game.board)
            print("Suggested move: {}".format(move_maximilian.position))
        last_move = get_human_move(game, last_move)
        if game.is_over:
            return game_over_bitch()
        print("\n===================  MAXIMILIANs TURN  ===================\n")
        move_maximilian, time_maximilian = maximilian.get_next_move(game.board)
        if human_vs_maximilian:
            game.record_new_move(move_maximilian)
            last_move = move_maximilian
            if game.is_over:
                return game_over_bitch()
            print("Maximilian's move: {}\nTime: {}".format(move_maximilian.position, time_maximilian))

def play_in_web(game, human_vs_maximilian, maximilian):
    print("LOOOOOOOOL")

if __name__ == "__main__":
    game = Game()
    terminal, human_vs_maximilian, suggestion = get_arguments()
    play_by_option = {
        True: play_in_terminal,
        False: play_in_web
    }
    try:
        load_hashtables()
        play_by_option[terminal](game, human_vs_maximilian, suggestion)
    except KeyboardInterrupt:
        pass
    save_hashtables()
    print("\nGood bye!")
