import argparse
import sys
from algo.maximilian import Maximilian
from algo.minmax_node import load_hashtables, save_hashtables
from algo.game import Game
from algo.move import Move
from algo.constants import WHITE, BLACK
from algo.errors import YouAreDumbException


def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("-t", "--terminal", action='store_true',
                        help="play using command line")
    return parser.parse_args()

def get_human_move():
    while True:
        try:
            move_string = input("Where would you like to play?\n")
            return Move(WHITE, move_string)
        except YouAreDumbException as e:
            print(e)


def play_in_terminal():
    game = Game()
    load_hashtables()
    while True:
        move_human = get_human_move()
        game.record_new_move(move_human)
        move_maximilian = Maximilian.get_next_move(game.board, move_human, game.captures)
        game.record_new_move(move_maximilian)
        print(move_maximilian.position)
        game.dump()
        save_hashtables()
    

if __name__ == "__main__":
    arguments = parse_arguments()
    if arguments.terminal:
        play_in_terminal()
    # else:
    #     play_in_web()
