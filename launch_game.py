import argparse
import sys
import time
from algo.maximilian import Maximilian
from algo.board import load_hashtables, save_hashtables
from algo.game import Game
from algo.move import Move
from algo.constants import WHITE, BLACK
from algo.errors import YouAreDumbException


def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("-t", "--terminal", action='store_true',
                        help="play using command line")
    parser.add_argument("-m", "--maximilian", action='store_true',
                        help="play using command line")
    return parser.parse_args()

def get_human_move(color):
    move_string = input("Where would you like to play?\n")
    return Move(color, move_string)

def play_in_terminal(human_vs_maximilian):
    game = Game()
    maximilian = Maximilian()
    load_hashtables()
    last_move = None
    try:
        while True:
            while True:
                try:
                    move_human = get_human_move(last_move.opposite_color if last_move else BLACK)
                    game.record_new_move(move_human)
                    last_move = move_human
                    break
                except YouAreDumbException:
                    pass
            game.dump()
            if game.is_over:
                print("It's over bitch.")
                break
            a = time.time()
            move_maximilian = maximilian.get_next_move(game.board)
            b = time.time()
            print("Time: %f" % (b - a))
            if human_vs_maximilian:
                game.record_new_move(move_maximilian)
                game.dump()
                last_move = move_maximilian
                if game.is_over:
                    print("It's over bitch.")
                    break
                print("Computer's move: ", move_maximilian.position, sep="")
            else:
                print("Suggested move: ", move_maximilian.position, sep="")
    except KeyboardInterrupt:
        pass
    save_hashtables()
    print("\nGood bye!")
    

if __name__ == "__main__":
    arguments = parse_arguments()
    if arguments.terminal:
        play_in_terminal(arguments.maximilian)
    # else:
    #     play_in_web()
